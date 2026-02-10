"""Lexer for a tiny Python subset using PLY.
Handles indentation by preprocessing lines and emitting INDENT/DEDENT tokens.
"""
import re
from typing import Iterator, List, Optional
import ply.lex as lex


class IndentLexer:
    # Token names required by PLY
    tokens = (
        "NAME",
        "NUMBER",
        "STRING",
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "ASSIGN",
        "LPAREN",
        "RPAREN",
        "COLON",
        "GT",
        "LT",
        "GE",
        "LE",
        "EQ",
        "NEQ",
        "NEWLINE",
        "INDENT",
        "DEDENT",
        "PRINT",
        "IF",
        "ELSE",
    )

    # Literal token regex rules
    t_PLUS = r"\+"
    t_MINUS = r"-"
    t_TIMES = r"\*"
    t_DIVIDE = r"/"
    t_ASSIGN = r"="
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_COLON = r":"
    t_GT = r">"
    t_LT = r"<"
    t_GE = r">="
    t_LE = r"<="
    t_EQ = r"=="
    t_NEQ = r"!="

    t_ignore = " \t"

    reserved = {
        "print": "PRINT",
        "if": "IF",
        "else": "ELSE",
    }

    def __init__(self) -> None:
        self.lexer = lex.lex(module=self, reflags=re.MULTILINE)
        self.indent_stack: List[int] = [0]
        self.current_line = 1

    # Match identifiers and check reserved words
    def t_NAME(self, t):
        r"[A-Za-z_]\w*"
        t.type = self.reserved.get(t.value, "NAME")
        return t

    # Integer numbers only for simplicity
    def t_NUMBER(self, t):
        r"\d+"
        t.value = int(t.value)
        return t

    def t_STRING(self, t):
        r'"([^\\"]|\\.)*"|\'([^\\\']|\\.)*\''
        # Strip quotes and unescape simple escapes
        text = t.value
        if text.startswith("\""):
            t.value = bytes(text[1:-1], "utf-8").decode("unicode_escape")
        elif text.startswith("\'"):
            t.value = bytes(text[1:-1], "utf-8").decode("unicode_escape")
        return t

    def t_COMMENT(self, t):
        r"\#.*"
        # Comments are ignored
        pass

    # Track line numbers
    def t_newline(self, t):
        r"\n+"
        self.current_line += len(t.value)

    def t_error(self, t):
        # Create a faux token representing the error to keep going
        message = f"Illegal character '{t.value[0]}' at line {self.current_line}"
        tok = lex.LexToken()
        tok.type = "ERROR"
        tok.value = message
        tok.lineno = self.current_line
        tok.lexpos = t.lexpos
        self.lexer.skip(1)
        return tok

    def _indent_tokens_for_line(self, leading_spaces: int) -> List[lex.LexToken]:
        tokens: List[lex.LexToken] = []
        current_indent = self.indent_stack[-1]
        if leading_spaces > current_indent:
            self.indent_stack.append(leading_spaces)
            tokens.append(self._make_token("INDENT"))
        elif leading_spaces < current_indent:
            while self.indent_stack and leading_spaces < self.indent_stack[-1]:
                self.indent_stack.pop()
                tokens.append(self._make_token("DEDENT"))
        return tokens

    def _make_token(self, token_type: str, value: Optional[str] = None) -> lex.LexToken:
        tok = lex.LexToken()
        tok.type = token_type
        tok.value = value if value is not None else token_type
        tok.lineno = self.current_line
        tok.lexpos = 0
        return tok

    def tokenize(self, data: str) -> Iterator[lex.LexToken]:
        """Generate tokens with indentation handling."""
        lines = data.splitlines(keepends=True)
        for raw_line in lines:
            line_text = raw_line.rstrip("\r\n")
            # Count leading spaces for indentation; tabs treated as 4 spaces
            leading_spaces = 0
            for ch in line_text:
                if ch == " ":
                    leading_spaces += 1
                elif ch == "\t":
                    leading_spaces += 4
                else:
                    break
            stripped = line_text.strip()
            indent_tokens: List[lex.LexToken] = []
            if stripped != "":
                indent_tokens = self._indent_tokens_for_line(leading_spaces)
            else:
                # Blank or whitespace-only line keeps indent unchanged
                pass

            # Tokenize the content portion
            content = line_text[leading_spaces:]
            self.lexer.lineno = self.current_line
            self.lexer.input(content)

            for tok in indent_tokens:
                yield tok

            while True:
                tok = self.lexer.token()
                if not tok:
                    break
                if tok.type == "ERROR":
                    yield tok
                    continue
                tok.lineno = self.current_line
                yield tok

            # Emit NEWLINE to separate logical lines
            yield self._make_token("NEWLINE", "\n")
            self.current_line += 1

        # After finishing, unwind any remaining indentation
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            yield self._make_token("DEDENT")

    def reset(self) -> None:
        self.indent_stack = [0]
        self.current_line = 1


def lex_source(source: str) -> List[lex.LexToken]:
    lexer = IndentLexer()
    tokens = list(lexer.tokenize(source))
    return tokens
