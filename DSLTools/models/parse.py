from typing import List, Optional
from enum import Enum


class VirtNodeType(Enum):
    NONTERMINAL = "box"
    TERMINAL = "diamond"
    KEYWORD = "oval"
    START = "plaintext"
    END = "point"


class GrammarElement:
    pass


class Terminal(GrammarElement):
    def __init__(self, value: str): self.value = value

    def __repr__(self): return f"'{self.value}'"


class NonTerminal(GrammarElement):
    def __init__(self, name: str): self.name = name

    def __repr__(self): return self.name


class Iteration(GrammarElement):
    def __init__(self, elements: List[GrammarElement], separator: Optional[Terminal] = None):
        self.elements = elements
        self.separator = separator

    def __repr__(self):
        sep = f" # {self.separator}" if self.separator else ""
        return f"{{ {' '.join(map(str, self.elements))} {sep} }}"


class Rule:
    def __init__(self, name: str):
        self.name = name
        self.alternatives: List[List[GrammarElement]] = []
