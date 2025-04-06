from enum import Enum
from abc import ABC, abstractmethod
from typing import Any
from DSLTools.models.IYamlMedia import IYamlMedia, YamlString


class Token(IYamlMedia):
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
                 evaln: IAttrEval = IdentityEval(),
                 terminalType: str = None,
                 str_value: str = None):

        self.terminalType: str = terminalType
        self.str: str = str_value

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

    SHIFT = 4

    def __blank(self, offset: int):
        return ' ' * self.SHIFT * offset

    def evaluated(self) -> Any:
        self.attribute = self.eval.calc(self.value)
        return self.attribute

    def __repr__(self):
        return f"Token({self.terminalType = }, {self.str = }, {self.token_type = }, '{self.value = }', pos: (l: {self.line}, c: {self.column}), {self.attribute = }"

    def to_yaml(self, offset: int = 0) -> YamlString:
        blank = self.__blank(offset)
        yaml = (
            blank + f"terminalType: '{self.terminalType or ''}'\n"
            + blank + f"token_type: '{self.token_type}'\n"
            + blank + f"value: '{self.value}'\n"
            + blank + f"attribute: '{self.attribute or ''}'\n"
        )
        return yaml


class Tokens(IYamlMedia):
    def __init__(self, tokens: list[Token]):
        self.__tokens = tokens

    def to_yaml(self, offset: int = 0) -> YamlString:
        yaml = 'tokens:\n'
        for token in self.__tokens:
            append = list(token.to_yaml(1))
            append[2] = '-'
            yaml += ''.join(append)
        return yaml


class GrammarToken:
    def __init__(self, value: str, token_type: str):
        self.value = value
        self.type = token_type
        self.attribute_type = None
