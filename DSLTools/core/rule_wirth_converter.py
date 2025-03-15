from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid
from DSLTools.models import Rule


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


def convert_rules_to_diagrams(rules: Dict[str, List[Rule]]) -> Dict[str, Diagram]:
    diagrams = {}

    for lhs, rule_list in rules.items():
        # Создаем диаграмму для каждого нетерминала
        start_node = Node(node_type='start', label=lhs)
        end_node = Node(node_type='end')
        current_node = start_node

        # Для всех альтернатив правила
        for rule in rule_list:
            alt_current = current_node
            for element in rule.elements:
                # Создаем узлы в зависимости от типа элемента
                if element['type'] == 'nonterminal':
                    new_node = Node(node_type='nonterminal', label=element['value'])
                elif element['type'] == 'terminal':
                    new_node = Node(node_type='terminal', label=element['value'])
                elif element['type'] == 'group':
                    new_node = create_group_diagram(element, diagrams)
                elif element['type'] == 'optional':
                    new_node = create_optional_diagram(element, diagrams)
                elif element['type'] == 'keyword':
                    new_node = Node(node_type='keyword', label=element['value'])

                # Связываем узлы
                alt_current.next_nodes.append(new_node)
                alt_current = new_node

            # Связываем конец альтернативы с конечным узлом
            alt_current.next_nodes.append(end_node)

        diagrams[lhs] = Diagram(
            start=start_node,
            end=end_node,
            nodes=collect_all_nodes(start_node)
        )

    return diagrams


def create_group_diagram(element: dict, diagrams: dict) -> Node:
    """Обрабатывает группы с сепараторами и циклами."""
    nodes = []
    for item in element["elements"]:
        node = create_node(item, diagrams)
        nodes.append(node)

    # Связываем элементы последовательно
    for i in range(len(nodes) - 1):
        nodes[i].next_nodes.append(nodes[i + 1])

    # Добавляем цикл и сепаратор
    if element.get("separator"):
        sep_node = Node(node_type="terminal", label=element["separator"])
        nodes[-1].next_nodes.append(sep_node)
        sep_node.next_nodes.append(nodes[0])
    else:
        nodes[-1].next_nodes.append(nodes[0])  # Простой цикл

    return nodes[0]


def create_optional_diagram(element: dict, diagrams: dict) -> Node:
    """Создает ветвление для опционального элемента."""
    main_node = create_node(element["elements"][0], diagrams)
    merge_node = Node(node_type="merge")

    # Ветвь с элементом
    main_node.next_nodes.append(merge_node)

    # Ветвь без элемента (пропуск)
    merge_node.next_nodes.append(merge_node)

    return main_node


def create_node(element: dict, diagrams: dict) -> Node:
    """Создает узлы для всех типов элементов."""
    if element["type"] == "nonterminal":
        return Node(node_type="nonterminal", label=element["value"])
    elif element["type"] == "terminal":
        return Node(node_type="terminal", label=element["value"])
    elif element["type"] == "keyword":
        return Node(node_type="keyword", label=element["value"])  # Ключевые слова как терминалы
    elif element["type"] == "group":
        return create_group_diagram(element, diagrams)
    elif element["type"] == "optional":
        return create_optional_diagram(element, diagrams)
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
