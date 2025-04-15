from pathlib import Path

from DSLTools.models.legacy_for_wirth import NodeLegacy, NodeTypeLegacy


def generate_graph_structure(vertex: list[NodeLegacy], matrix: list[list]) -> NodeLegacy:
    """Здесь будет функция по переводу в структуру, повторяющую GetSyntaxInfo"""
    pass

def transform_to_wirth_diag_type(node_type: NodeTypeLegacy):
    res = ""
    if node_type == NodeTypeLegacy.NONTERMINAL:
        res = "box"
    elif node_type == NodeTypeLegacy.TERMINAL:
        res = "diamond"
    elif node_type == NodeTypeLegacy.KEY:
        res = "oval"
    elif node_type == NodeTypeLegacy.END:
        res = "point"
    elif node_type == NodeTypeLegacy.START:
        res = "plaintext"
    return res

def generate_wirth_by_rule(vertex: list[NodeLegacy], matrix: list[list]) -> str:
    """Здесь будет перевод правила в диаграмму Вирта."""
    dot_lines = [
        f"digraph {vertex[0].str} {{",
    ]

    node_names = [vertex[0].type]
    node_names.extend([chr(ord("A") + i) for i, node in enumerate(vertex[1:-1])])
    node_names.append(vertex[-1].type)

    for node, node_name in zip(vertex, node_names):
        dot_lines.append(f'  {node_name} [label="{node.str}" shape={transform_to_wirth_diag_type(node.type)}];')
    N = len(matrix)

    edges = []
    for i in range(N):
        for j in range(N):
            if (matrix[i][j] != 0):
                edges.append((i, j))

    for edge in edges:
        dot_lines.append(f"{node_names[edge[0]]} -> {node_names[edge[1]]};")

    dot_lines.append("}")
    return "\n".join(dot_lines)
