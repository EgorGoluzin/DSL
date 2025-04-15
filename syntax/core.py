from enum import Enum


class SyntaxDescriptionType(Enum):
    VIRT_DIAGRAMS = "virt"
    RBNF = "rbnf"


class NodeType(Enum):
    TERMINAL = 0
    KEY = 1
    NONTERMINAL = 2
    START = 3
    END = 4


class Node:
    def __init__(self, type, str):
        self.type = type
        self.str = str
        self.nextNodes = []

    def __str__(self):
        res = f'Node: type = {self.type}; str = {self.str}; nextNodes = ['
        for i, node in enumerate(self.nextNodes):
            res += f'{i}: ' + str(node) + '; '
        return res + ']'

    def __repr__(self):
        res = f'Node: type = {self.type}; str = {self.str}; nextNodes = ['
        for i, node in enumerate(self.nextNodes):
            res += f'{i}: ' + str(node) + '; '
        return res + ']'
