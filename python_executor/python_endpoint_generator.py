from fastapi import FastAPI
from pydantic import BaseModel
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import traceback
import uvicorn
import math 

app = FastAPI(title="Python Code Executor")

# Shared global dictionary to store function definitions
exec_globals = {"math": math}

class CodeRequest(BaseModel):
    code: str
    test_cases: list[str] = []

class TestResult(BaseModel):
    passed: bool
    message: str

class CodeResponse(BaseModel):
    output: str
    test_results: list[TestResult]
    
@app.post("/execute", response_model=CodeResponse)
def execute_code(request: CodeRequest):
    stdout = StringIO()
    stderr = StringIO()
    test_results = []

    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            # Execute the function definition
            exec(request.code, exec_globals)

            # Execute each test case
            for index, test in enumerate(request.test_cases):
                try:
                    exec(test, exec_globals)
                    test_results.append({"passed": True, "message": f"Test passed: {test}"})
                except AssertionError as e:
                    test_results.append({"passed": False, "message": f"Assertion failed: {test}"})
                except Exception as e:
                    test_results.append({"passed": False, "message": f"Error in test case: {test}, Error: {str(e)}"})

    except Exception as e:
        return CodeResponse(
            output=stdout.getvalue(),
            test_results=[{"passed": False, "message": f"Code execution error: {str(e)}"}]
        )

    return CodeResponse(
        output=stdout.getvalue(),
        test_results=test_results
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
