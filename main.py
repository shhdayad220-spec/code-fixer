from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fixer import analyze_python, analyze_cpp

app = FastAPI(title="Code Fixer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    language: str
    code: str

@app.get("/")
def root():
    return {"message": "Code Fixer API is running"}

@app.post("/analyze")
def analyze_code(payload: CodeRequest):
    language = payload.language.lower().strip()

    if language == "python":
        return analyze_python(payload.code)
    if language in ["cpp", "c++"]:
        return analyze_cpp(payload.code)

    return {
        "success": False,
        "message": "Unsupported language. Use python or cpp.",
        "errors": [],
        "fixed_code": payload.code,
    }
