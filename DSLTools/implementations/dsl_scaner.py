import re
from typing import List

from dsl_info import Terminal, tokenRegularExpressions
from DSLTools.core.scanning import IScanner
from DSLTools.models.tokens import Token, TokenType


class DSLScanner(IScanner):
    def __init__(self):
        self._regexes = [
            (terminal, re.compile(pattern))
            for terminal, pattern in tokenRegularExpressions
        ]

    def tokenize(self, code: str) -> List[Token]:
        tokens = []
        pos = 0
        while pos < len(code):
            pos = self._skip_whitespace(code, pos)
            if pos >= len(code):
                break

            token, pos = self._match_token(code, pos)
            tokens.append(token)
        return tokens

    def _skip_whitespace(self, code: str, pos: int) -> int:
        return re.search(r'\S', code[pos:]).start() + pos if re.search(r'\S', code[pos:]) else len(code)

    def _match_token(self, code: str, pos: int) -> (Token, int):
        for terminal, regex in self._regexes:
            match = regex.match(code, pos)
            if match:
                return Token(
                    type=TokenType.TERMINAL,
                    terminal_type=terminal,
                    value=match.group()
                ), match.end()
        raise SyntaxError(f"Unrecognized token at position {pos}")