from dataclasses import dataclass, field
from enum import Enum
<<<<<<< HEAD
from collections.abc import Callable
from typing import Any, TypeVar
=======
from dsl_info import Terminal, Nonterminal
from typing import Union, List

>>>>>>> master


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


@dataclass
class ASTNode:
    type: NodeType         # Тип узла: терминал-нетерминал-ключ
    subtype: 'str'     # Подтип нетерминала или терминала - используемые в
    # вашем коде
    children: list = field(default_factory=list)   # Дочерние узлы
    value: str = ''       # Значение (для терминалов)
    attribute: Any = None
    position: tuple = None  # (line, column)
    evaluation: Callable[[str, list[TASTNode]], Any] = None
    # собственное значение, список значений дочерних узлов,
    # возвращаемый тип (любой)

    def evaluated(self):
        self.attribute = self.evaluation(self.value, self.children)
        return self.attribute
