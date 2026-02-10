"""Semantic analysis for the tiny Python subset."""
from __future__ import annotations
from typing import List, Set, Any

from . import parser as ast


class SymbolTable:
    def __init__(self) -> None:
        self.defined: Set[str] = set()

    def define(self, name: str) -> None:
        self.defined.add(name)

    def is_defined(self, name: str) -> bool:
        return name in self.defined

    def copy(self) -> "SymbolTable":
        clone = SymbolTable()
        clone.defined = set(self.defined)
        return clone


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.errors: List[str] = []

    def analyze(self, program: ast.Program) -> List[str]:
        self.errors = []
        symbols = SymbolTable()
        for stmt in program.statements:
            self._visit_statement(stmt, symbols)
        return self.errors

    def _visit_statement(self, node: Any, symbols: SymbolTable) -> None:
        if isinstance(node, ast.Assignment):
            self._visit_expr(node.expr, symbols)
            symbols.define(node.name)
        elif isinstance(node, ast.Print):
            self._visit_expr(node.expr, symbols)
        elif isinstance(node, ast.If):
            self._visit_expr(node.condition, symbols)
            body_table = symbols.copy()
            for stmt in node.body:
                self._visit_statement(stmt, body_table)
            if node.orelse is not None:
                else_table = symbols.copy()
                for stmt in node.orelse:
                    self._visit_statement(stmt, else_table)
        else:
            self.errors.append(f"Unknown statement type: {type(node).__name__}")

    def _visit_expr(self, node: Any, symbols: SymbolTable) -> None:
        if isinstance(node, ast.Number):
            return
        if isinstance(node, ast.String):
            return
        if isinstance(node, ast.Name):
            if not symbols.is_defined(node.id):
                self.errors.append(f"Undefined variable '{node.id}'")
            return
        if isinstance(node, ast.BinOp):
            self._visit_expr(node.left, symbols)
            self._visit_expr(node.right, symbols)
            return
        self.errors.append(f"Unknown expression type: {type(node).__name__}")


def analyze_semantics(program: ast.Program) -> List[str]:
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)
