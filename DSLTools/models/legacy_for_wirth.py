from enum import Enum


class NodeTypeLegacy(Enum):
    TERMINAL = 0
    KEY = 1
    NONTERMINAL = 2
    START = 3
    END = 4


class NodeLegacy:
    """Это старый объект узла правила, который нужно переработать."""
    def __init__(self, type, str_):

        self.type = type
        self.str = str_
        self.nextNodes = []

        self.nonterminal = str | None
        """Было динамически появляющимся полем, явно его здесь объявил. В случае если нетерминал будет не null."""
        self.terminal = str | None
        """Было динамически появляющимся полем, явно его здесь объявил. В случае если терминал будет не null"""
