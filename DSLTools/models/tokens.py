from enum import Enum


class Token:
    """Объект токена в потоке токенов. Посмотри класс Token.Type для
    уточнения."""
    class Type(str, Enum):
        """Тип токена. Есть только терминал и ключ, хотя в классе
        NodeType типов больше. Возможно, дублирование обосновано.
        У псевдокода прошлого года такое же дублирование."""
        TERMINAL = 'terminal'
        KEY = 'key'

    def __init__(self,
                 token_type: str,
                 value: Type = None,
                 line: int = None,
                 column: int = None):
        self.token_type = token_type  # Тип токена берем из грамматики.
        self.value = value  # Лексическое значение
        self.line = line  # Позиция в исходном коде
        self.column = column

    def __repr__(self):
        return f"Token({self.token_type}, '{self.value}', pos: (l: {self.line}, c: {self.column})"
