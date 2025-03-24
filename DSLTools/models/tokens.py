from enum import Enum
from abc import ABC, abstractmethod
from typing import Any


class Token:
    """Объект токена в потоке токенов. Посмотри класс Token.Type для
    уточнения."""
    class IAttrEval(ABC):
        """Интерфейс для класса, считающего значение атрибута в токене."""
        @abstractmethod
        def calc(self, value: str) -> Any:
            pass

    class IdentityEval(IAttrEval):
        def calc(self, value: str) -> Any:
            return value

    class Type(str, Enum):
        """Тип токена. Есть только терминал и ключ, хотя в классе
        NodeType типов больше. Возможно, дублирование обосновано.
        У псевдокода прошлого года такое же дублирование."""
        TERMINAL = 'terminal'
        KEY = 'key'

    def __init__(self,
                 token_type: Type | str,
                 value: str = None,
                 line: int = None,
                 column: int = None,
                 evaln: IAttrEval = IdentityEval()):
        self.token_type = token_type
        """Тип токена берем из грамматики."""
        self.value = value
        """Лексическое значение."""
        self.line = line
        """Позиция в исходном коде."""
        self.column = column
        """Позиция в исходном коде."""
        self.attribute = None
        """Поле под вычисляемый атрибут."""
        self.eval = evaln
        """Объект, вычисляющий атрибут токена."""

    def evaluated(self) -> Any:
        self.attribute = self.eval.calc(self.value)
        return self.attribute

    def __repr__(self):
        return f"Token({self.token_type}, '{self.value}', pos: (l: {self.line}, c: {self.column})"
