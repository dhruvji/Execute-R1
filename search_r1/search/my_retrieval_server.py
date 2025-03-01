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
    code: list[str]
    test_cases: list[list[str]] = []

class TestResult(BaseModel):
    passed: bool
    message: str

class CodeResponse(BaseModel):
    output: str = ""
    test_results: list[TestResult] = []
    
@app.post("/execute", response_model=list[CodeResponse])
def execute_code(request: CodeRequest):
    print("Received code request")
    print(request)

    stdout = StringIO()
    stderr = StringIO()
    outputs = [] 
    test_results = []
    ret = list()

    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            #print(f"Code to execute: {request.code}")
            # Execute the function definition
            for index, code in enumerate(request.code):
                response = CodeResponse()
                try:
                   exec(code, exec_globals)
                   response.output = stdout.getvalue()

                except Exception as e: 
                    response.output = str(e)

                tests = request.test_cases[index]
                for test in tests: 

                    # Execute each test case
                    try:
                        exec(test, exec_globals)
                        response.test_results.append({"passed": True, "message": f"Test passed: {test}"})
                    except AssertionError as e:
                        response.test_results.append({"passed": False, "message": f"Assertion failed: {test}"})
                    except Exception as e:
                        response.test_results.append({"passed": False, "message": f"Error in test case: {test}, Error: {str(e)}"})
                ret.append(response)


    except Exception as e:
        ret = [CodeResponse(output=f"{str(e)}", test_results=[]) for _ in range(len(request.code))]


    return ret

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
