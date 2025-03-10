from typing import List, Optional, Dict, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field


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

    def __str__(self) -> str:
        return f"Terminal(name: {self.name}, pattern: {self.pattern})"


@dataclass
class RuleElement:
    type: str  # "element", "group", "optional"
    value: Union[str, List[str]]  # Для "element" - строка, для "group"/"optional" - список
    separator: Optional[str] = None

    def __str__(self):

        return f"RuleEl(t: {self.type}\nvalue:{self.value}\nsep:{self.separator})"

@dataclass
class Rule:
    lhs: str
    elements: List[RuleElement]
    separator: Optional[str] = None

    # def __str__(self):
    #     return f"Rule( lhs = {self.lhs}, elements: " + "\n\t".join([el.__str__() for el in self.elements])\
    #         + f"\n\tsep={self.separator})"


@dataclass
class GrammarObject:
    terminals: Dict[str, Terminal] = field(default_factory=dict)
    keys: List[Tuple[str, str]] = field(default_factory=list)
    non_terminals: List[str] = field(default_factory=list)
    axiom: str = ''
    rules: Dict[str, List[Rule]] = field(default_factory=dict)

    def __post_init__(self):
        self._validate()

    def _validate(self):
        pass
        # Проверка аксиомы
        # if self.axiom not in self.non_terminals:
        #     raise ValueError(f"Axiom '{self.axiom}' is not a defined non-terminal")
        #
        # # Проверка правил
        # for nt, rule in self.rules.items():
        #     if nt not in self.non_terminals:
        #         raise ValueError(f"Undefined non-terminal in rule: {nt}")

        # Проверка уникальности терминалов и ключей
        # all_symbols = [t.name for t in self.terminals.values()] + [k[0] for k in self.keys]
        # if len(all_symbols) != len(set(all_symbols)):
        #     raise ValueError("Duplicate terminal/key definitions")

    def get_terminals_for_template(self) -> str:
        return "\n\t" + "\n\t".join([f"{item} = '{item}'" for item in self.terminals.keys()])

    def get_regular_expression_for_template(self):
        return ",\n\t".join([f"(Terminal.{item.name}, r'{item.pattern}')" for item in self.terminals.values()])

    def get_keys_for_template(self):
        return ",\n\t".join([f"('{item[1]}', Terminal.{item[0]})" for item in self.keys])

    def get_non_terminals_for_template(self):
        return "\n\t" + "\n\t".join([f"{item} = '{item}'"for item in self.non_terminals])

    def __str__(self):
        res = "GrammarObject(\n\tTerminals:"
        res += "\n\t\t" + "\n\t\t".join([item.__str__() for item in self.terminals.values()]) + ";"
        ## TODO: Создать класс для ключей
        res += "\n\tKeys:" + "\n\t\t" + "\n\t\t".join([f"type: {item[0]}, val: {item[1]}" for item in self.keys]) + ";"
        res += "\n\tNonTerminals:" + "\n\t\t" + "\n\t\t".join(self.non_terminals) + ";"
        res += "\n\tRules:" + "\n\t\t" + "\n\t\t".join(["| ".join([rule.__str__() for rule in item]) for item in self.rules.values()]) + ";"
        res += "\n\tAxiom:" + f"\n\t\t{self.axiom}"
        return res

"""
GrammarObject(
        Terminals:
                Terminal(name: number, pattern: [1-9]\d*)
                Terminal(name: operation, pattern: [\+\*])
                Terminal(name: terminator, pattern: ,);
        Keys:
                type: operation, val: +
                type: operation, val: *
                type: terminator, val: ,;
        NonTerminals:
                EXPRESSIONS
                EXPRESSION
                TERM;
        Rules:
                Rule(lhs: EXPRESSIONS els: ['EXPRESSION'] sep: ,)
                Rule(lhs: EXPRESSION els: ['TERM'] sep: +)
                Rule(lhs: TERM els: ['number'] sep: *);
        Axiom:
                EXPRESSIONS
"""