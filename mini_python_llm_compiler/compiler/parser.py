"""Parser for the tiny Python subset using PLY yacc."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple, Any
import ply.yacc as yacc

from .lexer import IndentLexer


# AST node definitions
@dataclass
class Program:
    statements: List[Any]


@dataclass
class Assignment:
    name: str
    expr: Any


@dataclass
class Print:
    expr: Any


@dataclass
class If:
    condition: Any
    body: List[Any]
    orelse: Optional[List[Any]]


@dataclass
class BinOp:
    left: Any
    op: str
    right: Any


@dataclass
class Number:
    value: int


@dataclass
class String:
    value: str


@dataclass
class Name:
    id: str


class TinyPythonParser:
    tokens = IndentLexer.tokens

    # Operator precedence
    precedence = (
        ("left", "GT", "LT", "GE", "LE", "EQ", "NEQ"),
        ("left", "PLUS", "MINUS"),
        ("left", "TIMES", "DIVIDE"),
    )

    def __init__(self) -> None:
        self.lexer = IndentLexer()
        self.errors: List[str] = []
        self.parser = yacc.yacc(module=self, start="program", debug=False)

    def parse(self, source: str) -> Tuple[Optional[Program], List[str]]:
        self.errors = []
        self.lexer.reset()
        try:
            result = self.parser.parse(lexer=self.lexer.tokenize(source))
        except Exception as exc:  # pylint: disable=broad-except
            self.errors.append(str(exc))
            result = None
        return result, self.errors

    # Grammar rules
    def p_program(self, p):
        """program : statements"""
        p[0] = Program(p[1])

    def p_statements_multi(self, p):
        """statements : statements statement"""
        p[0] = p[1] + [p[2]] if p[2] is not None else p[1]

    def p_statements_single(self, p):
        """statements : statement"""
        p[0] = [] if p[1] is None else [p[1]]

    def p_statement_simple(self, p):
        """statement : simple NEWLINE"""
        p[0] = p[1]

    def p_statement_if(self, p):
        """statement : if_statement"""
        p[0] = p[1]

    def p_statement_empty(self, p):
        """statement : NEWLINE"""
        p[0] = None

    def p_simple_assignment(self, p):
        """simple : NAME ASSIGN expression"""
        p[0] = Assignment(name=p[1], expr=p[3])

    def p_simple_print(self, p):
        """simple : PRINT LPAREN expression RPAREN"""
        p[0] = Print(expr=p[3])

    def p_if_statement_if(self, p):
        """if_statement : IF comparison COLON NEWLINE INDENT statements DEDENT"""
        p[0] = If(condition=p[2], body=p[6], orelse=None)

    def p_if_statement_if_else(self, p):
        """if_statement : IF comparison COLON NEWLINE INDENT statements DEDENT ELSE COLON NEWLINE INDENT statements DEDENT"""
        p[0] = If(condition=p[2], body=p[6], orelse=p[12])

    def p_comparison(self, p):
        """comparison : expression GT expression
                       | expression LT expression
                       | expression GE expression
                       | expression LE expression
                       | expression EQ expression
                       | expression NEQ expression"""
        p[0] = BinOp(left=p[1], op=p[2], right=p[3])

    def p_expression_binop(self, p):
        """expression : expression PLUS expression
                       | expression MINUS expression
                       | expression TIMES expression
                       | expression DIVIDE expression"""
        p[0] = BinOp(left=p[1], op=p[2], right=p[3])

    def p_expression_group(self, p):
        """expression : LPAREN expression RPAREN"""
        p[0] = p[2]

    def p_expression_number(self, p):
        """expression : NUMBER"""
        p[0] = Number(value=p[1])

    def p_expression_string(self, p):
        """expression : STRING"""
        p[0] = String(value=p[1])

    def p_expression_name(self, p):
        """expression : NAME"""
        p[0] = Name(id=p[1])

    def p_error(self, token):
        if token:
            self.errors.append(f"Syntax error at '{token.value}' (line {token.lineno})")
        else:
            self.errors.append("Syntax error at EOF")


def parse_source(source: str) -> Tuple[Optional[Program], List[str]]:
    parser = TinyPythonParser()
    return parser.parse(source)
