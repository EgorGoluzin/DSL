from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid
from DSLTools.models import Rule, ElementType, RuleElement


@dataclass
class Node:
    node_type: str  # 'start', 'end', 'nonterminal', 'terminal', 'group', 'optional'
    label: str = ""
    next_nodes: List['Node'] = field(default_factory=list)
    edge_label: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Diagram:
    start: Node
    end: Node
    nodes: Dict[str, Node] = field(default_factory=dict)


def convert_rules_to_diagrams(rules: Dict[str, Rule]) -> Dict[str, Diagram]:
    diagrams = {}

    for lhs, rule_list in rules.items():
        # Создаем диаграмму для каждого нетерминала
        start_node = Node(node_type='start', label=lhs)
        end_node = Node(node_type='end')
        current_node = start_node

        start_sequence = rule_list.rpart
        # Пробегаемся по правилам внешней последовательности
        for rule in start_sequence.value:
            if rule.type == ElementType.NONTERMINAL:
                new_node = Node(node_type='nonterminal', label=rule.value)
            elif rule.type == ElementType.TERMINAL:
                new_node = Node(node_type='terminal', label=rule.value)
            elif rule.type == ElementType.GROUP:
                new_node = create_group_diagram(rule, rule, current_node)
            elif rule.type == ElementType.OPTIONAL:
                new_node = create_optional_diagram(rule, start_sequence.value, current_node)
                current_node = current_node.next_nodes[-1]
                break
            elif rule.type == ElementType.KEYWORD:
                new_node = Node(node_type='keyword', label=rule.value)
            # Связываем узлы
            current_node.next_nodes.append(new_node)
            current_node = new_node

            # Связываем конец альтернативы с конечным узлом
        current_node.next_nodes.append(end_node)

        diagrams[lhs] = Diagram(
            start=start_node,
            end=end_node,
            nodes=collect_all_nodes(start_node)
        )

    return diagrams


def create_group_diagram(element: RuleElement, rule, current_node) -> Node:
    """Обрабатывает группы с сепараторами и циклами."""
    nodes = []
    for item in element.value:
        node = create_node(item, rule, current_node)
        nodes.append(node)

    # Связываем элементы последовательно
    for i in range(len(nodes) - 1):
        nodes[i].next_nodes.append(nodes[i + 1])
    sep = element.separator
    # Добавляем цикл и сепаратор
    if sep:
        # TODO: Добавить нормально separator. То есть там должно быть понимание кто это терминал или нет
        sep_node = create_node(sep, rule, current_node)
        nodes[-1].next_nodes.append(sep_node)
        sep_node.next_nodes.append(nodes[0])
    else:
        nodes[-1].next_nodes.append(nodes[0])  # Простой цикл

    return nodes[0]


def find_next_element(element: RuleElement, rule: list[RuleElement]):
    for i, el in enumerate(rule):
        if el.type == element.type and el.value == element.value:
            return rule[i + 1]


def find_prev_element(element: RuleElement, rule: list[RuleElement]):
    for i, el in enumerate(rule):
        if el.type == element.type and el.value == element.value:
            return rule[i - 1]


def create_optional_diagram(optional_element: RuleElement, rule, current_node: Node) -> Node:
    """Создает ветвление для опционального элемента."""
    # Обработка элементов внутри опционального блока
    start_node_in_optional = create_node(optional_element.value[0], rule, current_node)
    last_node_in_optional = start_node_in_optional

    nodes = []
    for i in range(1, len(optional_element.value)):
        node = create_node(optional_element.value[i], optional_element.value, start_node_in_optional)
        nodes.append(node)

    if len(nodes):
        for node in nodes:
            last_node_in_optional.next_nodes.append(node)
            last_node_in_optional = node

    element_after_optional = create_node(find_next_element(optional_element, rule), rule, current_node)
    last_node_in_optional.next_nodes.append(element_after_optional)
    current_node.next_nodes.append(start_node_in_optional)
    current_node.next_nodes.append(element_after_optional)
    return start_node_in_optional


def create_node(element: RuleElement, rule, current_node) -> Node:
    """Создает узлы для всех типов элементов."""
    if element.type == ElementType.NONTERMINAL:
        return Node(node_type="nonterminal", label=element.value)
    elif element.type == ElementType.TERMINAL:
        return Node(node_type="terminal", label=element.value)
    elif element.type == ElementType.KEYWORD:
        return Node(node_type="keyword", label=element.value)  # Ключевые слова как терминалы
    elif element.type == ElementType.GROUP:
        return create_group_diagram(element, rule, current_node)
    elif element.type == ElementType.OPTIONAL:
        return create_optional_diagram(element, rule, current_node)
    else:
        raise ValueError(f"Unknown element type: {element['type']}")


def collect_all_nodes(start_node: Node) -> Dict[str, Node]:
    nodes = {}
    stack = [start_node]

    while stack:
        node = stack.pop()
        if node.id not in nodes:
            nodes[node.id] = node
            stack.extend(node.next_nodes)

    return nodes
