from dataclasses import dataclass
from enum import Enum
from dsl_info import Terminal, Nonterminal
from typing import Union



class NodeType(Enum):
    NONTERMINAL = 'nonterminal'
    TERMINAL = 'terminal'
    KEY = 'key'



class TreeNode:
    def __init__(self, node_type, nonterminal_type=None, attribute=None):
        self.type = node_type
        self.nonterminal_type = nonterminal_type
        self.attribute = attribute
        self.childs = []


@dataclass
class ASTNode:
    type: NodeType          # Тип узла: терминал-нетерминал-ключ
    subtype: Union[Terminal, Nonterminal] = None     # Подтип нетерминала или терминала
    children: list = []   # Дочерние узлы
    value: str = ''       # Значение (для терминалов)
    position: tuple = None  # (line, column)
