from DSLTools.models import Diagram


def generate_dot(diagram: Diagram) -> str:
    """Генерирует DOT-файл. Эта магическая функция должна сконвертировать Diagram -> строки файл .dot"""
    dot_lines = [
        f"digraph {diagram.start.label.upper()} {{",
        "  rankdir=LR;",
        "  node [fontname=\"Arial\"];",
        f'  start [label="{diagram.start.label}" shape=plaintext];',
        '  end [label="" shape=point];'
    ]

    # Исключаем branch, merge, start и end
    main_nodes = [
        n for n in diagram.nodes.values()
        if n.node_type not in ("start", "end", "branch", "merge")
    ]

    # Назначаем имена узлам: A, B, C...
    node_names = {node.id: chr(ord("A") + i) for i, node in enumerate(main_nodes)}

    # Добавляем узлы
    for node in main_nodes:
        name = node_names[node.id]
        if node.node_type == "nonterminal":
            dot_lines.append(f'  {name} [label="{node.label}" shape=box];')
        elif node.node_type == "terminal":
            dot_lines.append(f'  {name} [label="{node.label}" shape=diamond];')
        elif node.node_type == "keyword":
            dot_lines.append(f'  {name} [label="{node.label}" shape=oval];')

    # Добавляем связи
    for node in diagram.nodes.values():
        if node.node_type == "start":
            for next_node in node.next_nodes:
                if next_node.id in node_names:
                    dot_lines.append(f'  start -> {node_names[next_node.id]};')
        elif node.id in node_names:
            for next_node in node.next_nodes:
                if next_node.node_type == "end":
                    dot_lines.append(f'  {node_names[node.id]} -> end;')
                elif next_node.id in node_names:
                    dot_lines.append(f'  {node_names[node.id]} -> {node_names[next_node.id]};')

    dot_lines.append("}")
    return "\n".join(dot_lines)
