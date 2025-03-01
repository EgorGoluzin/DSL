from typing import List, Optional, Dict
from enum import Enum
from dataclasses import dataclass


class VirtNodeType(Enum):
    NONTERMINAL = "box"
    TERMINAL = "diamond"
    KEYWORD = "oval"
    START = "plaintext"
    END = "point"


class GrammarElement:
    pass


@dataclass
class Terminal:
    name: str
    pattern: str


@dataclass
class Rule:
    lhs: str
    elements: List[str]
    separator: Optional[str] = None


@dataclass
class GrammarObject:
    terminals: Dict[str, Terminal]
    keys: List[str]
    non_terminals: List[str]
    axiom: str
    rules: Dict[str, Rule]
