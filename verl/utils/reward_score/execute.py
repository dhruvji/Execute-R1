import re
import random
import requests
import json


def extract_solution(solution_str):
    """Extract the equation from the solution string."""
    # Remove everything before the first "Assistant:"
    # if "Assistant:" in solution_str:
    #     solution_str = solution_str.split("Assistant:", 1)[1]
    # elif "<|im_start|>assistant" in solution_str:
    #     solution_str = solution_str.split("<|im_start|>assistant", 1)[1]
    # else:
    #     return None
    # solution_str = solution_str.split('\n')[-1]

    answer_pattern = r'<answer>(.*?)</answer>'
    match = re.finditer(answer_pattern, solution_str, re.DOTALL)
    matches = list(match)
    
    # If there are 0 or exactly 1 matches, return None
    if len(matches) <= 2:
        return None
    
    # If there are 2 or more matches, return the last one
    return matches[-1].group(1).strip()


def compute_scores(batch_solutions, batch_ground_truths, method='strict', format_score=0.1, score=1.):
    """Batch scoring function for python code execution."""
    
    batch_payloads = []
    for solution_str, ground_truth in zip(batch_solutions, batch_ground_truths):
        code = extract_solution(solution_str=solution_str)
        
        if code is None:
            batch_payloads.append(None)
            continue
        
        batch_payloads.append({
            "code": code,
            "test_cases": ground_truth['test_cases']
        })
    
    results = []
    
    # Send batch request
    for payload in batch_payloads:
        if payload is None:
            results.append(format_score)
            continue
        
        try:
            response = requests.post(
                "http://127.0.0.1:8000/execute",  # Should be configurable
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            result = response.json()

            if result.get("error"):
                results.append(format_score)
                continue

            test_results = result.get("test_results", [])
            if not test_results:
                results.append(format_score)
                continue

            passed_tests = sum(1 for test in test_results if test["passed"])
            total_tests = len(test_results)
            final_score = format_score + (score - format_score) * (passed_tests / total_tests) if total_tests > 0 else format_score

            results.append(final_score)
        
        except (requests.RequestException, ValueError) as e:
            results.append(format_score)
            continue
    
    return results
