"""Compiler orchestrating lexing, parsing, and semantic analysis."""
from __future__ import annotations
from typing import Dict, Any

from .parser import parse_source, Program
from .semantic import analyze_semantics


def compile_source(source: str) -> Dict[str, Any]:
    """Run parser and semantic analyzer and collect errors."""
    ast, syntax_errors = parse_source(source)
    semantic_errors = []
    if ast and not syntax_errors:
        semantic_errors = analyze_semantics(ast)
    return {
        "ast": ast,
        "syntax_errors": syntax_errors,
        "semantic_errors": semantic_errors,
    }


def compile_and_print(source: str) -> None:
    """Convenience for CLI debugging."""
    result = compile_source(source)
    print("Syntax errors:", result["syntax_errors"])
    print("Semantic errors:", result["semantic_errors"])


__all__ = ["compile_source", "compile_and_print", "Program"]
