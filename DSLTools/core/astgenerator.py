import re
from typing import List, TypeVar
import graphviz
from copy import deepcopy

from _elementtree import ParseError

from DSLTools.models import (GrammarObject, Token, ASTNode, Rule, IAstBuilder, IAstRender)
from DSLTools.models.ast import NodeType
from DSLTools.models.legacy_for_wirth import NodeLegacy, NodeTypeLegacy


TWalkStep = TypeVar('TWalkStep', bound='WalkStep')


class WalkStep:
    def __init__(
        self,
        parent_state: TWalkStep = None,
        pos: int = 0,
        node: NodeLegacy = [],
        rule_index: int = 0,
        nonterm: str = '',
        depth: int = -1,
    ):
        self.parent_state = parent_state
        self.pos = pos
        self.node = node
        self.rule_index = rule_index
        self.nonterm = nonterm
        self.depth = depth

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'Step: pos = {self.pos}, nonterminal: {self.nonterm}'


class DefaultAstBuilder(IAstBuilder):
    def __init__(self, debug: bool = False):
        self.states: list[WalkStep] = []
        self.go: GrammarObject = None
        self.tokens: list[Token] = []
        self.end: int = 0
        self.axiom: str = ''
        self._debug = debug
        self.__logs: list[str] = []
        self.depth: int = 0

    def __ret(self):
        # print('States:')
        # print(self.states)
        snap = deepcopy(self.states)
        self.states[-1].rule_index += 1
        # print(f'Init last state: {self.states[-1].nonterm}')
        while self.states[-1].rule_index >= len(self.states[-1].node.nextNodes):
            self.states.pop()
            # print(f'New last state: {self.states[-1].nonterm}')
            self.depth -= 1
            # print(f'Depleted depth by 1 in RET, now {self.depth = }')
            if len(self.states) == 0:
                print(self.__ast)
                error = f'Current token: {self.tokens[snap[-1].pos].repr()}\r\n'
                self._log_ret(error)
                error += 'States to crash:\r\n'
                for step in snap:
                    info = str(step)
                    error += f'{info}\r\n'
                    self._log_ret(info)
                raise Exception(f"Ran out of states: \r\n{error}")
            self.states[-1].rule_index += 1

    def __walk(self):
        self.states = [
            WalkStep(
                node=self.go.syntax_info[self.axiom], nonterm=self.axiom,
                depth=0
            )
        ]
        counter = 0
        limit = 100
        while True:
            counter += 1
            print(f'Iteration {counter}')
            if counter == limit:
                print(f'Counter reached {limit = }')
                raise Exception(f'Counter reached {limit = }')
            state = self.states[-1]
            pos = state.pos
            node = state.node
            depth = state.depth
            rule = node.nextNodes[state.rule_index]
            # print(f'{state.nonterm = }, {rule[0].type.value}, {rule[0].nonterminal = }, {rule[0].terminal = }, {rule[0].str = }')

            if NodeType.END == rule[0].type:
                self._walk_details(pos, depth, rule[0].type.value, rule[0].nonterminal)
                self._print_last_log()
                parent_state = state.parent_state
                self.depth -= 1
                # print(f'Depleted depth by 1 in END, now {self.depth = }')
                if parent_state is None:
                    if pos == self.end:
                        return
                    else:
                        # print(f'{parent_state.nonterm = }')
                        self.__ret()
                        continue
                # print(f'{parent_state.nonterm = }')
                if parent_state.parent_state is not None:
                    None
                    # print(f'{parent_state.parent_state.nonterm = }')
                # self.depth -= 1
                self.states.append(
                    WalkStep(
                        parent_state.parent_state,
                        pos,
                        parent_state.node.nextNodes[parent_state.rule_index][0],
                        0,
                        parent_state.nonterm,
                        parent_state.parent_state.depth if parent_state.parent_state else 0
                    )
                )
                continue
            elif NodeType.NONTERMINAL == rule[0].type:
                self._walk_details(pos, depth, rule[0].type.value, rule[0].nonterminal)
                self._print_last_log()
                    # self._log_walk(f'Pos: {pos}, {rule[0].type} branch, Rule for: {rule[0].nonterminal}, token: {self.tokens[pos].repr()}')
                if rule[0].nonterminal not in self.go.syntax_info:
                    raise Exception(f"Failed to find '{rule[0].nonterminal}' description in {self.go.syntax_info}\r\nCurrent token: {self.tokens[pos].repr()}")
                self.states.append(
                    WalkStep(
                        state,
                        pos,
                        self.go.syntax_info[rule[0].nonterminal],
                        0,
                        rule[0].nonterminal,
                        depth + 1
                    )
                )
                self.depth += 1
                continue
            if pos >= self.end:
                self.__ret()
                continue
            new_token = self.tokens[pos]
            if NodeType.KEY == rule[0].type and Token.Type.KEY == new_token.token_type and new_token.str == rule[0].str:
                self._walk_details(pos, depth, rule[0].type.value, rule[0].str)
                # print(f'Current nonterm for this terminal: {state.nonterm}')
                self._print_last_log()
                self.states.append(
                    WalkStep(
                        state.parent_state,
                        pos + 1,
                        rule[0],
                        0,
                        state.nonterm,
                        state.depth
                    )
                )
                # self.depth -= 1
                continue
            elif NodeType.TERMINAL == rule[0].type and Token.Type.TERMINAL == new_token.token_type and new_token.terminalType == rule[0].terminal:
                self._walk_details(pos, depth, rule[0].type.value, rule[0].terminal)
                self._print_last_log()
                # print(f'Current nonterm for this terminal: {state.nonterm}')
                self.states.append(
                    WalkStep(
                        state.parent_state,
                        pos + 1,
                        rule[0],
                        0,
                        state.nonterm,
                        state.depth
                    )
                )
                self.depth -= 1
                continue
            # print(f'Reached type mismatch on {pos = }, {state.nonterm = }')
            self.__ret()
            continue

    def build(self, go: GrammarObject, tokens: List[Token]) -> ASTNode:
        self.go = go
        self.tokens = tokens
        self.end = len(self.tokens)
        self.axiom = self.go.axiom

        ast = ASTNode(ASTNode.Type.NONTERMINAL, self.axiom)
        self.__ast = ast
        ast.nonterminalType = self.axiom
        nodes_stack = [ast]
        self.__walk()
        for state in self.states:
            pos = state.pos
            node = state.node
            rule = node.nextNodes[state.rule_index]
            if NodeType.END == rule[0].type:
                parent_state = state.parent_state
                if parent_state is None:
                    if pos == self.end:
                        nodes_stack[-1].commands.append(rule[1])
                        return ast
                    else:
                        raise Exception(f"Reached an end node, but {pos = }, {self.end = }")
                nodes_stack[-1].commands.append(rule[1])
                nodes_stack.pop()
                continue
            elif NodeType.NONTERMINAL == rule[0].type:
                if rule[0].nonterminal not in self.go.syntax_info:
                    raise Exception(f"Failed to find '{rule[0].nonterminal}' description in {self.go.syntax_info = }")
                new_nonterm = ASTNode(ASTNode.Type.NONTERMINAL, rule[0].nonterminal)
                new_nonterm.nonterminalType = rule[0].nonterminal
                nodes_stack[-1].children.append(new_nonterm)
                nodes_stack[-1].commands.append(rule[1])
                node = rule[0]
                nodes_stack.append(new_nonterm)
                continue
            if pos >= self.end:
                raise Exception(f"{pos = } exceeded {self.end = }")
            new_token = self.tokens[pos]
            if NodeType.KEY == rule[0].type and Token.Type.KEY == new_token.token_type and new_token.str == rule[0].str:
                element = ASTNode(ASTNode.Type.TOKEN, new_token.str)
                element.attribute = new_token.attribute
                element.value = new_token.str
                element.token = new_token
                nodes_stack[-1].children.append(element)
                nodes_stack[-1].commands.append(rule[1])
                continue
            elif NodeType.TERMINAL == rule[0].type and Token.Type.TERMINAL == new_token.token_type and new_token.terminalType == rule[0].terminal:
                element = ASTNode(ASTNode.Type.TOKEN, new_token.terminalType)
                element.attribute = new_token.attribute
                element.value = new_token.value
                element.token = new_token
                nodes_stack[-1].children.append(element)
                nodes_stack[-1].commands.append(rule[1])
                continue
            raise Exception(f"Current state of {rule = } and {new_token = } does not satisfy any of the cases.")
        return ast

    def _log(self, message: str):
        """Логирование процесса построения"""
        if self._debug:
            built = f"[Builder] {message}"
            self.__logs.append(built)
            print(built)

    def _log_method(self, method: str, msg: str):
        if self._debug:
            built = f'[Builder.{method}] {msg}'
            self.__logs.append(built)
            # print(built)

    def _print_last_log(self):
        if self.__logs:
            print(self.__logs[-1])

    def _log_walk(self, msg: str):
        self._log_method('walk', msg)

    def _walk_details(self, pos: int, depth: int, branch: str, val: str):
        if pos < self.end:
            self._log_walk(f'{pos = }, {depth = }, {branch = }, rule for: {val}, token: {self.tokens[pos].repr()}')

    def _log_build(self, msg: str):
        self._log_method('build', msg)

    def _log_ret(self, msg: str):
        self._log_method('ret', msg)

    def logs(self) -> list[str]:
        return self.__logs


class DefaultAstRenderer(IAstRender):
    def visualize(self, go: GrammarObject, tokens: List[Token]):
        # Шаг 1: Построить AST из GrammarObject и токенов
        parser = GeneralizedParser(go)
        ast = parser.parse(tokens)

        # Шаг 2: Создать граф с помощью graphviz
        diagram_name = "ast_visualization"
        h = graphviz.Digraph(diagram_name, format='svg')
        h.attr(rankdir='TB')  # Сверху вниз для читаемости

        # Шаг 3: Обойти AST и построить граф
        i = 1
        nodes = [(ast, 0)]  # (узел, ID родителя)
        while nodes:
            node, parent_id = nodes.pop(0)

            # Определяем тип узла и его форму
            if node.type in go.non_terminals:
                # Нетерминал
                label = f"NONTERMINAL\ntype: {node.type}"
                if node.value:
                    label += f"\nvalue: {node.value}"
                h.node(str(i), label, shape='box')
            elif node.type in go.terminals:
                # Терминал
                label = f"TERMINAL\ntype: {node.type}\nvalue: {node.value}"
                h.node(str(i), label, shape='diamond')
            elif any(key[0] == node.type for key in go.keys):
                # Ключ
                label = f"KEY\nstring: {node.value}"
                h.node(str(i), label, shape='oval')
            else:
                # Неизвестный тип (на всякий случай)
                label = f"UNKNOWN\ntype: {node.type}\nvalue: {node.value}"
                h.node(str(i), label, shape='ellipse')

            # Связываем с родителем, если он есть
            if parent_id != 0:
                h.edge(str(parent_id), str(i))

            # Добавляем детей в очередь
            nodes.extend((child, i) for child in node.children)
            i += 1

        # Шаг 4: Сохраняем и рендерим граф
        output_dir = "debug_ast"  # Можно сделать параметром, если нужно
        h.render(directory=output_dir, view=True, cleanup=False)  # Оставляем .gv файл для отладки


class GeneralizedParser:
    def __init__(self, grammar: GrammarObject):
        self.grammar = grammar
        self.tokens = []
        self.pos = 0
        self._debug = True  # Включить логирование

    def parse(self, tokens: List[Token]) -> ASTNode:
        self.tokens = tokens
        self.pos = 0
        return self._parse_non_terminal(self.grammar.axiom)

    def _log(self, message: str):
        """Логирование процесса парсинга"""
        if self._debug:
            print(f"[Parser] {message}")

    def _parse_non_terminal(self, non_terminal: str) -> ASTNode:
        self._log(f"Parsing {non_terminal} at position {self.pos}")
        node = ASTNode(type=non_terminal, children=[])
        original_pos = self.pos

        for rule in self.grammar.rules.get(non_terminal, []):
            self._log(f"Trying rule: {' '.join(rule.elements)}")
            temp_pos = self.pos
            try:
                temp_children = []
                for element in rule.elements:
                    self._log(f"Processing element: {element}")

                    # Обработка составных элементов (например: 'Variable' ':' 'Expression')
                    if self._is_quoted(element):
                        self._consume_keyword(element.strip("'\""))

                    elif element in self.grammar.non_terminals:
                        temp_children.append(self._parse_non_terminal(element))

                    else:
                        self._consume_terminal(element)

                    temp_children.append(self._create_current_node(element))

                # Обработка разделителя
                if rule.separator:
                    self._log(f"Processing separator: {rule.separator}")
                    while self._peek_token().value == rule.separator:
                        self._consume_keyword(rule.separator)
                        temp_children.append(self._create_current_node(rule.separator))
                        # Повтор элементов правила
                        for element in rule.elements:
                            if self._is_quoted(element):
                                self._consume_keyword(element.strip("'\""))
                            elif element in self.grammar.non_terminals:
                                temp_children.append(self._parse_non_terminal(element))
                            else:
                                self._consume_terminal(element)
                            temp_children.append(self._create_current_node(element))

                node.children = temp_children
                return node

            except ParseError as e:
                self._log(f"Rule failed: {str(e)}")
                self.pos = temp_pos  # Откат
                continue

        raise ParseError(f"No rules matched for {non_terminal} at position {original_pos}")

    def _is_quoted(self, s: str) -> bool:
        """Проверяет, является ли элемент строкой в кавычках"""
        return len(s) > 1 and s[0] in ("'", '"') and s[-1] == s[0]

    def _consume_keyword(self, keyword: str):
        """Обработка ключевых слов и символов"""
        current_token = self._peek_token()
        expected_types = [kt[0] for kt in self.grammar.keys if kt[1] == keyword]

        if not expected_types:
            raise ParseError(f"Keyword '{keyword}' not defined in grammar")

        if current_token.value != keyword:
            raise ParseError(
                f"Expected keyword '{keyword}', got '{current_token.value}' "
                f"at {current_token.line}:{current_token.column}"
            )

        self.pos += 1

    def _consume_terminal(self, terminal_type: str):
        """Обработка обычных терминалов"""
        current_token = self._peek_token()
        if current_token.token_type != terminal_type:
            raise ParseError(
                f"Expected {terminal_type}, got {current_token.token_type} "
                f"at {current_token.line}:{current_token.column}"
            )
        self.pos += 1

    def _create_current_node(self, element: str) -> ASTNode:
        """Создает узел для текущего элемента"""
        if self._is_quoted(element):
            return ASTNode(
                type="keyword",
                value=element.strip("'\""),
                position=(self.tokens[self.pos - 1].line, self.tokens[self.pos - 1].column)
            )
        else:
            return ASTNode(
                type=element,
                value=self.tokens[self.pos - 1].value,
                position=(self.tokens[self.pos - 1].line, self.tokens[self.pos - 1].column)
            )

    def _peek_token(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
# class GeneralizedParser:
#     def __init__(self, grammar: GrammarObject):
#         self.grammar = grammar
#         self.tokens = []
#         self.pos = 0
#
#     def parse(self, tokens: List[Token]) -> ASTNode:
#         self.tokens = tokens
#         self.pos = 0
#         return self._parse_non_terminal(self.grammar.axiom)
#
#     def _parse_non_terminal(self, non_terminal: str) -> ASTNode:
#         node = ASTNode(type=non_terminal, children=[])
#         original_pos = self.pos
#
#         for rule in self.grammar.rules.get(non_terminal, []):
#             try:
#                 temp_children = []
#                 temp_pos = self.pos
#
#                 for element in rule.elements:
#                     if element in self.grammar.non_terminals:
#                         # Нетерминал: рекурсивный вызов
#                         temp_children.append(self._parse_non_terminal(element))
#                     else:
#                         # Терминал: проверяем текущий токен
#                         self._consume_terminal(element)
#                         temp_children.append(ASTNode(
#                             type=element,
#                             value=self.tokens[self.pos - 1].value,
#                             position=(self.tokens[self.pos - 1].line,
#                                       self.tokens[self.pos - 1].column)
#                         ))
#
#                 node.children = temp_children
#                 return node
#
#             except ParseError:
#                 self.pos = temp_pos  # Откат для следующего правила
#                 continue
#
#         raise ParseError(f"Could not parse {non_terminal} at pos {self.pos}")
#
#     def _consume_terminal(self, expected_type: str):
#         if self.pos >= len(self.tokens):
#             raise ParseError(f"Unexpected EOF, expected {expected_type}")
#
#         current_token = self.tokens[self.pos]
#
#         # Ищем подходящий тип терминала
#         if any(
#                 t_type == expected_type
#                 for t_type, t_value in self.grammar.keys
#                 if t_value == current_token.value
#         ) or current_token.token_type == expected_type:
#             self.pos += 1
#         else:
#             raise ParseError(
#                 f"Expected {expected_type}, got {current_token.token_type} "
#                 f"at line {current_token.line}:{current_token.column}"
#             )