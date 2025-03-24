from typing import Dict
from DSLTools.models import Rule, ElementType, RuleElement, RuleWirthNode, Diagram


def convert_rules_to_diagrams(rules: Dict[str, Rule]) -> Dict[str, Diagram]:
    diagrams = {}

    for lhs, rule_list in rules.items():
        # Создаем диаграмму для каждого нетерминала
        start_node = RuleWirthNode(node_type='start', label=lhs)
        end_node = RuleWirthNode(node_type='end')
        current_node = start_node
        new_node = None
        start_sequence = rule_list.rpart
        # Пробегаемся по правилам внешней последовательности
        for rule in start_sequence.value:
            if rule.type == ElementType.NONTERMINAL:
                new_node = RuleWirthNode(node_type='nonterminal', label=rule.value)
            elif rule.type == ElementType.TERMINAL:
                new_node = RuleWirthNode(node_type='terminal', label=rule.value)
            elif rule.type == ElementType.KEYWORD:
                new_node = RuleWirthNode(node_type='keyword', label=rule.value)
            elif rule.type == ElementType.GROUP:
                new_node = create_group_diagram(rule, current_node)
                ## Таким образом дабавим к текущему узлу начальный из группы (цикла)
                # current_node.next_nodes.append(new_node.next_nodes[0])
                current_node = new_node
                continue
            elif rule.type == ElementType.OPTIONAL:
                current_node = create_optional_diagram(rule, current_node)
                continue
            elif rule.type == ElementType.ALTERNATIVE:
                current_node = create_alternative_diagram(rule, current_node)
                continue

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


def create_group_diagram(element: RuleElement, current_node: RuleWirthNode) -> RuleWirthNode:
    """Обрабатывает группы с сепараторами и циклами."""
    # Привязываем текущий элемент к первому элементу группы
    start_group_node = create_node(element.value[0], current_node)
    cur_node = start_group_node
    # Пробегаемся по элементам группы.
    # Здесь автоматом происходит их привязка.
    for i in range(1, len(element.value)):
        node = create_node(element.value[i], cur_node)
        cur_node = node

    sep = element.separator
    # Добавляем цикл и сепаратор
    if sep:
        # TODO: Нашел пример TERMINAL_BLOCK в описании RBNF
        # Привязывае к последнему в группе узлу и затем связываем с начальным.
        sep_node = create_node(sep, cur_node)
        sep_node.next_nodes.append(start_group_node)
    else:
        cur_node.next_nodes.append(start_group_node)
    # Простой цикл
    # Выдаем последний узел в цикле
    return cur_node


def find_next_element(element: RuleElement, rule: list[RuleElement]):
    for i, el in enumerate(rule):
        if el.type == element.type and el.value == element.value:
            return rule[i + 1]


def find_prev_element(element: RuleElement, rule: list[RuleElement]):
    for i, el in enumerate(rule):
        if el.type == element.type and el.value == element.value:
            return rule[i - 1]


def create_optional_diagram(optional_element: RuleElement, current_node: RuleWirthNode) -> RuleWirthNode:
    """Создает ветвление для опционального элемента."""

    # Обработка элементов внутри опционального блока
    cur_node = current_node
    start_node_in_optional = create_node(optional_element.value[0], cur_node)
    last_node_in_optional = start_node_in_optional

    for i in range(1, len(optional_element.value)):
        node = create_node(optional_element.value[i], last_node_in_optional)
        last_node_in_optional = node

    element_after_optional = create_node(RuleElement(type=ElementType.MERGE_FLAG, value="optional"),
                                         last_node_in_optional)
    # element_after_optional.next_nodes.append(current_node)
    current_node.next_nodes.append(element_after_optional)
    return element_after_optional


def create_alternative_diagram(alternative_element: RuleElement, current_node: RuleWirthNode) -> RuleWirthNode:
    alternative_mark = RuleWirthNode(node_type=ElementType.ALTERNATIVE_FLAG.value, label="")
    ## Для осознания, сколько детей будет подвязано добавим первым элементом
    # в current_node alternative
    current_node.next_nodes.append(alternative_mark)
    for i in range(len(alternative_element.value)):
        node = create_node(alternative_element.value[i], current_node)
        node.next_nodes.append(alternative_mark)
    return alternative_mark


def create_node(element: RuleElement, current_node: RuleWirthNode) -> RuleWirthNode:
    """Создает узлы для всех типов элементов.
    При этом привязываем очередной новый узел к текущему.

    Входящие аргументы:
        element(RuleElement): новый элемент, который будем привязывать к current_node.\n
        rule(list[RuleElement]): условно контекст, в котором рассматривается element.
            Используется для доступа к следующему элементу после element в optional_diagram.
        current_node(RuleWirthNode): текущий узел, к которому осуществляется привязка.
        """
    if element.type == ElementType.NONTERMINAL:
        new_node = RuleWirthNode(node_type="nonterminal", label=element.value)
        current_node.next_nodes.append(new_node)
        return new_node
    elif element.type == ElementType.TERMINAL:
        new_node = RuleWirthNode(node_type="terminal", label=element.value)
        current_node.next_nodes.append(new_node)
        return new_node
    elif element.type == ElementType.KEYWORD:
        new_node = RuleWirthNode(node_type="keyword", label=element.value)
        current_node.next_nodes.append(new_node)
        return new_node
    elif element.type == ElementType.GROUP:
        new_node = create_group_diagram(element, current_node)
        return new_node
    elif element.type == ElementType.OPTIONAL:
        return create_optional_diagram(element, current_node)
    elif element.type == ElementType.ALTERNATIVE:
        create_alternative_diagram(element, current_node)
    elif element.type == ElementType.MERGE_FLAG:
        new_node = RuleWirthNode(node_type=ElementType.MERGE_FLAG.value, label="")
        current_node.next_nodes.append(new_node)
        return new_node
    else:
        raise ValueError(f"Unknown element type: {element['type']}")


def clean_up_tree(cur_node: RuleWirthNode, father: RuleWirthNode):
    if cur_node.node_type == ElementType.MERGE_FLAG.value:
        start_el = cur_node.next_nodes[0]
        start_el.next_nodes.append(cur_node.next_nodes[-1])
        father.next_nodes.remove(cur_node)


def collect_all_nodes(start_node: RuleWirthNode) -> Dict[str, RuleWirthNode]:
    def find_optional(next_elements: list[RuleWirthNode]):
        for i, it in enumerate(next_elements):
            if it.node_type == ElementType.MERGE_FLAG.value:
                return i

    def find_alternative(next_elements: list[RuleWirthNode]):
        for i, it in enumerate(next_elements):
            if it.node_type == ElementType.ALTERNATIVE_FLAG.value:
                return i

    def optional_proc(element_with_optional: RuleWirthNode) -> RuleWirthNode:
        index = find_optional(element_with_optional.next_nodes)
        optional = element_with_optional.next_nodes.pop(index)
        # TODO: Придумать обработку для 2-ух и более последовательных optional
        next_node = optional.next_nodes[-1]
        # next_node.next_nodes.extend(optional.next_nodes[:-1])
        element_with_optional.next_nodes.append(next_node)
        return element_with_optional

    def alternative_proc(element_with_alternative: RuleWirthNode) -> RuleWirthNode:
        # Тот самый элемент alternative, который лежит в начале альтернативного блока
        index = find_alternative(element_with_alternative.next_nodes)
        alternative = element_with_alternative.next_nodes.pop(index)
        ## Вот тут надо на примерах понять, стоит намутить
        # ещё hendler для рекурсивной обработки сложных случаев.
        element_with_alternative.next_nodes.append(alternative.next_nodes[-1])
        return element_with_alternative

    def check_is_optional_mark(node_el: RuleWirthNode) -> bool:
        return any([item.node_type == ElementType.MERGE_FLAG.value for item in node_el.next_nodes])

    def check_is_alternative(node_el: RuleWirthNode):
        return any([item.node_type == ElementType.ALTERNATIVE_FLAG.value for item in node_el.next_nodes])

    nodes = {}
    stack = [start_node]
    while stack:
        node = stack.pop()
        if node.id not in nodes:
            if check_is_optional_mark(node):
                # Если зашли в элемент содержащий в одном из своих узлов метку "optional"
                # Тогда вызываем функцию по обработке op_el
                node = optional_proc(node)
                nodes[node.id] = node
                stack.extend(node.next_nodes)
                continue
            if check_is_alternative(node):
                node = alternative_proc(node)
                nodes[node.id] = node
                stack.extend(node.next_nodes)
                continue

            nodes[node.id] = node
            stack.extend(node.next_nodes)

    return nodes
