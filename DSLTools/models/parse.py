import re
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
    keys: List[tuple[str, str]]
    non_terminals: List[str]
    axiom: str
    rules: Dict[str, Rule]

    ## TODO: Mb... Refactor data class with template getters
    def get_terminals_for_template(self) -> str:
        return "\n\t" + "\n\t".join([f"{item} = '{item}'" for item in self.terminals.keys()])

    def get_regular_expression_for_template(self):
        return ",\n\t".join([f"(Terminal.{item.name}, r'{item.pattern}')" for item in self.terminals.values()])

    def get_keys_for_template(self):
        return ",\n\t".join([f"('{item[1]}', Terminal.{item[0]})" for item in self.keys])

    def get_non_terminals_for_template(self):
        return "\n\t" + "\n\t".join([f"{item} = '{item}'"for item in self.non_terminals])

"""
GrammarObject(terminals={
    'number': Terminal(name='number', pattern='[1-9]\\d*'), 
    'operation': Terminal(name='operation', pattern='[\\+\\*]'), 
    'terminator': Terminal(name='terminator', pattern=',')}, 
    keys=['+', '*', ','], 
    non_terminals=['EXPRESSIONS', 'EXPRESSION', 'TERM'], 
    axiom='EXPRESSIONS', 
    rules={'EXPRESSIONS': Rule(lhs='EXPRESSIONS', elements=['EXPRESSION'], separator=','), 
    'EXPRESSION': Rule(lhs='EXPRESSION', elements=['TERM'], separator='+'), 
    'TERM': Rule(lhs='TERM', elements=['number'], separator='*')})

"""