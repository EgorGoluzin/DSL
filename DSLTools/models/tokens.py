from enum import Enum


class Token:
    def __init__(self,
                 token_type: str,
                 value: str = None,
                 position: int = None):
        self.type = token_type  # Тип токена берем из грамматики.
        self.value = value  # Лексическое значение
        self.position = position  # Позиция в исходном коде

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', pos: {self.position})"
