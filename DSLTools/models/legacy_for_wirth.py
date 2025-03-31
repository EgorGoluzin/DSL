from enum import Enum


class NodeTypeLegacy(str, Enum):
    TERMINAL = 'terminal'
    KEY = 'key'
    NONTERMINAL = 'nonterminal'
    START = 'start'
    END = 'end'


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
    
    def __str__(self):
        res = (
            f"type: {self.type}; " +
            f'str: {self.str}; ' +
            f'nonterminal: {self.nonterminal}; ' +
            f'terminal: {self.terminal}; '
        )
        res += 'nextNodes: ['
        for node in self.nextNodes:
            res += f'{node}'
        return res + ']'
    
    def __repr__(self):
        res = (
            f"type: {self.type}; " +
            f'str: {self.str}; ' +
            f'nonterminal: {self.nonterminal}; ' +
            f'terminal: {self.terminal}; '
        )
        res += 'nextNodes: ['
        for node in self.nextNodes:
            res += f'{node}'
        return res + ']'
