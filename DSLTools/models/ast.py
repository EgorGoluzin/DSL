from dataclasses import dataclass
from enum import Enum

class NodeType(Enum):
    NONTERMINAL = 1
    TERMINAL = 2

class TreeNode:
    def __init__(self, node_type, nonterminal_type=None, attribute=None):
        self.type = node_type
        self.nonterminal_type = nonterminal_type
        self.attribute = attribute
        self.childs = []

@dataclass
class ASTNode:
    type: str          # Тип узла (нетерминал)
    children: list     # Дочерние узлы
    value: str = None  # Значение (для терминалов)
    position: tuple = None  # (line, column)
