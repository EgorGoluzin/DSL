from enum import Enum


class NodeTypeLegacy(str, Enum):
    TERMINAL = 'terminal'
    KEY = 'key'
    NONTERMINAL = 'nonterminal'
    START = 'start'
    END = 'end'


class NodeLegacy:
    """Это старый объект узла правила, который нужно переработать."""
    def __init__(self, type, str_, nextNodes=None):

        self.type = type
        self.str = str_
        self.nextNodes: list | None = (nextNodes, [])[nextNodes is None]

        self.nonterminal: str | None = None
        """Было динамически появляющимся полем, явно его здесь объявил. В случае если нетерминал будет не null."""
        self.terminal: str | None = None
        """Было динамически появляющимся полем, явно его здесь объявил. В случае если терминал будет не null"""

    def __str__(self):
        res = (
            "NodeLegacy("
            f"type= '{self.type}', " +
            f"str_= '{self.str}', " +
            f"nonterminal='{self.nonterminal}', " +
            f"terminal='{self.terminal}', "
        )
        res += 'nextNodes=['
        for node in self.nextNodes:
            res += f'{node}'
        return res + '])'

    def __repr__(self):
        res = (
            "NodeLegacy("
            f"type= '{self.type}', " +
            f"str_= '{self.str}', " +
            f"nonterminal= '{self.nonterminal}', " +
            f"terminal= '{self.terminal}', "
        )
        res += 'nextNodes= ['
        for node in self.nextNodes:
            res += f'{node}'
        return res + '])'
