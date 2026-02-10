"""FastAPI backend exposing LLM generation and compiler checks."""
from __future__ import annotations
from typing import Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel

from compiler.compiler import compile_source
from llm.llm_generator import generate_code, LLMGenerator

app = FastAPI(title="Mini Python LLM Compiler")


class PromptRequest(BaseModel):
    prompt: str


class CodeRequest(BaseModel):
    code: str


@app.post("/generate_code")
def api_generate_code(body: PromptRequest) -> Dict[str, str]:
    generator = LLMGenerator()
    code = generator.generate_code(body.prompt)
    return {"code": code}


@app.post("/compile_code")
def api_compile_code(body: CodeRequest) -> Dict[str, Any]:
    result = compile_source(body.code)
    return {
        "syntax_errors": result["syntax_errors"],
        "semantic_errors": result["semantic_errors"],
    }


# Convenience root
@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "Mini Python LLM Compiler API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.api:app", host="0.0.0.0", port=8000, reload=False)
