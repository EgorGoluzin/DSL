from dataclasses import dataclass, field
from enum import Enum
from collections.abc import Callable
from typing import Any, TypeVar, NewType
from abc import ABC, abstractmethod


class NodeType(str, Enum):
    NONTERMINAL = 'nonterminal'
    TERMINAL = 'terminal'
    KEY = 'key'
    END = 'end'


class TreeNode:
    def __init__(self, node_type, nonterminal_type=None, attribute=None):
        self.type = node_type
        self.nonterminal_type = nonterminal_type
        self.attribute = attribute
        self.childs = []


TASTNode = TypeVar('TASTNode', bound='ASTNode')


class IASTNode(ABC):
    """Элемент абстрактного синтаксического дерева."""
    @abstractmethod
    def evaluated(self):
        pass


JsonString = NewType('JsonString', str)


class IJsonMedia(ABC):
    """Объект, преобразуемый в формат JSON."""
    @abstractmethod
    def to_json(self, offset: int = 0) -> JsonString:
        pass


@dataclass
class ASTNode(IASTNode, IJsonMedia):
    type: NodeType         # Тип узла: терминал-нетерминал-ключ
    subtype: 'str' = ''    # Подтип нетерминала или терминала - используемые в
    # вашем коде
    children: list[TASTNode] = field(default_factory=list)   # Дочерние узлы
    value: str = ''       # Значение (для терминалов)
    attribute: Any = None
    position: tuple = None  # (line, column)
    evaluation: Callable[[str, list[TASTNode]], Any] = None
    # собственное значение, список значений дочерних узлов,
    # возвращаемый тип (любой)
    SHIFT = 4


    def __blank(self, offset: int):
        return ' ' * self.SHIFT * offset

    def evaluated(self):
        self.attribute = self.evaluation(self.value, self.children)
        return self.attribute

    def json_no_newline(self, offset: int):
        json = (
            self.__blank(offset) + '{\n'
            + self.__blank(offset + 1) + f"type: '{self.type}',\n"
            + self.__blank(offset + 1) + f"subtype: '{self.subtype}',\n"
            + self.__blank(offset + 1) + f"value: '{self.value}',\n"
            + self.__blank(offset + 1) + f"attribute: '{'' if self.attribute is None else self.attribute}',\n"
            + self.__blank(offset + 1) + 'children: ['
        )
        if self.children == []:
            json += ']\n' + self.__blank(offset) + '}'
        else:
            json += '\n'
            for child in self.children[:-1]:
                json += child.json_no_newline(offset + 2) + ',\n'
            json += self.children[-1].json_no_newline(offset + 2) + '\n'
            json += self.__blank(offset + 1) + ']\n' + self.__blank(offset) + '}'
        return json

    def to_json(self, offset: int = 0) -> JsonString:
        return self.json_no_newline(offset) + '\n'
