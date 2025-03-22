import uuid
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class RuleWirthNode:
    """Класс узла диаграммы вирта.
    Для перевода GrammarObject.rules -> Диаграмму вирта правила -> GetSyntaxInfo(Legacy Function)"""

    ## Пока node_type это строка, так или иначе эти значения
    # почти полностью повторяют значения ElementType

    node_type: str  # 'start', 'end', 'nonterminal', 'terminal', 'group', 'optional'
    label: str = ""
    next_nodes: List['RuleWirthNode'] = field(default_factory=list)
    edge_label: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Diagram:
    start: RuleWirthNode
    end: RuleWirthNode
    nodes: Dict[str, RuleWirthNode] = field(default_factory=dict)