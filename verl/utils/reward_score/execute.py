import re
import random
import requests
import json


def extract_solution(solution_str):
    # Remove everything before the first "Assistant:"
    if "Assistant:" in solution_str:
        solution_str = solution_str.split("Assistant:", 1)[1]
    else:
        return None

    answer_pattern = r'<answer>(.*?)</answer>'
    match = re.finditer(answer_pattern, solution_str)
    matches = list(match)
    if matches:
        final_answer = matches[-1].group(1).strip()
    else:
        final_answer = None
    return final_answer


def compute_score(solution_str, ground_truth, method='strict', format_score=0.1, score=1.):
    """The scoring function for python code execution.
    
    Args:
        solution_str: the solution text containing code in <answer> tags
        ground_truth: dict containing 'target' (reference solution) and 'test_cases' (list of test cases)
        method: the method to extract the solution, choices are 'strict' and 'flexible'
        format_score: minimum score for providing valid code
        score: maximum score for passing all tests
    """
    code = extract_solution(solution_str=solution_str)
    do_print = random.randint(1, 64) == 1

    if do_print:
        print(f"--------------------------------")
        print(f"Solution code: {code}")
        print(f"Test cases: {ground_truth['test_cases']}")

    if code is None:
        if do_print:
            print(f"No code found in answer tags")
        return 0

    # Prepare execution request
    payload = {
        "code": code,
        "test_cases": ground_truth['test_cases']
    }

    try:
        # Send code to execution server
        response = requests.post(
            "http://127.0.0.1:8000/execute",  # Should be configurable
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        result = response.json()

        # Check for execution errors
        if result.get("error"):
            if do_print:
                print(f"Execution error: {result['error']}")
            return format_score

        # Calculate score based on passing tests
        test_results = result.get("test_results", [])
        if not test_results:
            if do_print:
                print("No test results returned")
            return format_score

        passed_tests = sum(1 for test in test_results if test["passed"])
        total_tests = len(test_results)
        
        # Scale score between format_score and full score based on passing tests
        if total_tests == 0:
            final_score = format_score
        else:
            final_score = format_score + (score - format_score) * (passed_tests / total_tests)

        if do_print:
            print(f"Passed {passed_tests}/{total_tests} tests")
            print(f"Final score: {final_score}")

        return final_score

    except (requests.RequestException, json.JSONDecodeError) as e:
        if do_print:
            print(f"Error during execution: {str(e)}")
        return format_score
