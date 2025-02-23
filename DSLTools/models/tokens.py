from enum import Enum


class TokenType(Enum):
    TERMINAL = 1
    KEYWORD = 2
    NONTERMINAL = 3


class Token:
    def __init__(self,
                 type: TokenType,
                 value: str = None,
                 terminal_type: str = None,
                 keyword: str = None,
                 attribute: object = None):
        self.type = type
        self.value = value
        self.terminal_type = terminal_type
        self.keyword = keyword
        self.attribute = attribute
