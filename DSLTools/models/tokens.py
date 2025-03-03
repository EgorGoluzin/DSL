from enum import Enum


class Token:
    def __init__(self,
                 token_type: str,
                 value: str = None,
                 line: int = None,
                 column: int = None):
        self.token_type = token_type  # Тип токена берем из грамматики.
        self.value = value  # Лексическое значение
        self.line = line  # Позиция в исходном коде
        self.column = column

    def __repr__(self):
        return f"Token({self.token_type}, '{self.value}', pos: (l: {self.line}, c: {self.column})"
