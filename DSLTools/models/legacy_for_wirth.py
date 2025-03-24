from enum import Enum


class NodeTypeLegacy(Enum):
    TERMINAL = 0
    KEY = 1
    NONTERMINAL = 2
    START = 3
    END = 4


class NodeLegacy:
    def __init__(self, type, str):
        self.type = type
        self.str = str
        self.nextNodes = []