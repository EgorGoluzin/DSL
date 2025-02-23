import pydot
from collections import defaultdict
from typing import Dict, List, Union, Optional, Set, Tuple
import pathlib
from DSLTools.models.parse import Rule, Terminal, GrammarElement, VirtNodeType, Iteration

class VirtParser:
    def __init__(self, diagrams_dir: str):
        self.diagrams_dir = pathlib.Path(diagrams_dir)
        self.rules: Dict[str, Rule] = {}
        self.edges: Dict[str, List[Tuple[str, Optional[Terminal]]]] = defaultdict(list)
        self.node_map: Dict[str, Union[GrammarElement, VirtNodeType]] = {}

    def parse(self) -> Dict[str, Rule]:
        for dot_file in self.diagrams_dir.glob("*.gv"):
            self._process_diagram(dot_file)
        return self.rules

    def _process_diagram(self, file_path: pathlib.Path):
        graph = pydot.graph_from_dot_file(str(file_path))[0]
        self._init_graph_data(graph)

        rule_name = graph.get_name().strip('"')
        rule = Rule(rule_name)

        start_node = next(k for k, v in self.node_map.items() if v == VirtNodeType.START)
        end_node = next(k for k, v in self.node_map.items() if v == VirtNodeType.END)

        self._find_and_replace_cycles()
        self._generate_alternatives(rule, start_node, end_node)

        if not rule.alternatives:
            raise ValueError(f"Rule {rule.name} is empty")

        self.rules[rule_name] = rule

    def _init_graph_data(self, graph: pydot.Dot):
        self.edges.clear()
        self.node_map.clear()

        # Обработка узлов
        for node in graph.get_nodes():
            node_name = node.get_name().strip('"')
            shape = node.get_shape() or "box"
            label = node.get_label().strip('"') or node_name

            if shape == VirtNodeType.START.value:
                self.node_map[node_name] = VirtNodeType.START
            elif shape == VirtNodeType.END.value:
                self.node_map[node_name] = VirtNodeType.END
            elif shape == VirtNodeType.NONTERMINAL.value:
                self.node_map[node_name] = VirtNodeType(label)
            elif shape in (VirtNodeType.TERMINAL.value, VirtNodeType.KEYWORD.value):
                self.node_map[node_name] = Terminal(label)

        # Обработка рёбер
        for edge in graph.get_edges():
            src = edge.get_source().strip('"')
            dst = edge.get_destination().strip('"')
            label = edge.get_label().strip('"') if edge.get_label() else None
            self.edges[src].append((dst, Terminal(label) if label else None))

    def _find_and_replace_cycles(self):
        visited: Set[str] = set()
        cycles = []

        def dfs(node: str, path: List[str]):
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return

            visited.add(node)
            for neighbor, _ in self.edges.get(node, []):
                dfs(neighbor, path + [node])
            visited.remove(node)

        for node in self.node_map:
            if node not in visited:
                dfs(node, [])

        # Обработка циклов
        for cycle in cycles:
            if len(cycle) > 1:
                self._replace_cycle_with_iteration(cycle)

    def _replace_cycle_with_iteration(self, cycle: List[str]):
        if len(cycle) < 3:
            return  # Цикл должен содержать как минимум стартовый узел и два элемента

        main_node = cycle[0]
        elements = []
        separators = []

        # Собираем элементы цикла и разделители
        for i in range(1, len(cycle) - 1):
            current_node = cycle[i]
            edge = next((e for e in self.edges[cycle[i - 1]] if e[0] == current_node), None)
            if edge:
                separators.append(edge[1])
            elements.append(self.node_map[current_node])

        # Заменяем главный узел на итерацию
        self.node_map[main_node] = Iteration(
            elements=elements,
            separator=separators[0] if separators else None
        )

        # Обновляем связи, удаляя цикличные переходы
        self.edges[main_node] = [
            (dst, label)
            for dst, label in self.edges[main_node]
            if dst not in cycle
        ]

    def _generate_alternatives(self, rule: Rule, start: str, end: str):
        visited = set()

        def traverse(node: str, path: List[GrammarElement], edge_label: Optional[Terminal]):
            new_path = path.copy()

            # Добавляем метку ребра
            if edge_label is not None:
                new_path.append(edge_label)

            # Добавляем узел (если не старт/конец)
            if node not in {start, end}:
                elem = self.node_map.get(node)
                if isinstance(elem, GrammarElement):
                    new_path.append(elem)

            # Если достигли конца, сохраняем путь
            if node == end:
                if new_path:
                    rule.alternatives.append(new_path)
                return

            if node in visited:
                return

            visited.add(node)
            for neighbor, label in self.edges.get(node, []):
                traverse(neighbor, new_path, label)
            visited.remove(node)

        traverse(start, [], None)

        # Проверяем, что есть хотя бы одна альтернатива
        if not rule.alternatives:
            raise ValueError(f"Rule {rule.name} is empty")


class RBNFGenerator:
    @staticmethod
    def generate(rule: Rule) -> str:
        lines = []
        for alt in rule.alternatives:
            parts = []
            for elem in alt:
                if isinstance(elem, Iteration):
                    iter_part = f"{{ {' '.join(map(str, elem.elements))}"
                    if elem.separator:
                        iter_part += f" # {elem.separator}"
                    iter_part += " }"
                    parts.append(iter_part)
                else:
                    parts.append(str(elem))
            lines.append(" ".join(parts))
        return f"{rule.name} ::= " + " |\n    ".join(lines) + " ."


# Пример использования
parser = VirtParser(r"C:\Users\Hp\PycharmProjects\DSL\_examples\expression\\")
grammar = parser.parse()

for rule_name, rule in grammar.items():
    print(RBNFGenerator.generate(rule))