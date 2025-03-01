from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import traceback
import uvicorn


app = FastAPI(title="Python Code Executor")

class CodeRequest(BaseModel):
    code: str

class CodeResponse(BaseModel):
    output: str
    error: str | None = None
    
@app.post("/execute", response_model=CodeResponse)
def execute_code(request: CodeRequest):
    # Capture stdout and stderr
    stdout = StringIO()
    stderr = StringIO()
    
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            # Execute the code in a safe environment
            exec(request.code, {}, {})
            
        return CodeResponse(
            output=stdout.getvalue(),
            error=stderr.getvalue() if stderr.getvalue() else None
        )
    except Exception as e:
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        return CodeResponse(
            output=stdout.getvalue(),
            error=error_msg
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
