import re
from typing import List, TypeVar
import graphviz

from _elementtree import ParseError

from DSLTools.models import (GrammarObject, Token, ASTNode, Rule, IAstBuilder, IAstRender)
from DSLTools.models.ast import NodeType


TWalkStep = TypeVar('TWalkStep', bound='WalkStep')
class WalkStep:
    def __init__(
        self,
        parent_state: TWalkStep = None,
        pos: int = 0,
        node: list = [],
        rule_index: int = 0,
        nonterm: str = ''
    ):
        self.parent_state = parent_state
        self.pos = pos
        self.node = node
        self.rule_index = rule_index
        self.nonterm = nonterm


class DefaultAstBuilder(IAstBuilder):
    def __init__(self):
        self.states: list[WalkStep] = []
        self.go: GrammarObject = None
        self.tokens: list[Token] = []
        self.end: int = 0
        self.axiom: str = ''

    def __ret(self):
        self.states[-1].rule_index += 1
        while self.states[-1].rule_index >= len(self.states[-1].node.nextNodes):
            self.states.pop()
            if len(self.states) == 0:
                raise Exception("Ran out of states")
            self.states[-1].rule_index += 1

    def __walk(self):
        self.states = [
            WalkStep(
                node=self.go.syntax_info[self.axiom], nonterm=self.axiom
            )
        ]
        while True:
            state = self.states[-1]
            pos = state.pos
            node = state.node
            rule = node.nextNodes[state.rule_index]

            if NodeType.END == rule[0].type:
                parent_state = state.parent_state
                if parent_state is None:
                    if pos == self.end:
                        return
                    else:
                        self.__ret()
                        continue
                self.states.append(
                    WalkStep(
                        parent_state.parent_state,
                        pos,
                        parent_state.node.nextNodes[parent_state.rule_index][0],
                        0,
                        parent_state.nonterm
                    )
                )
                continue
            elif NodeType.NONTERMINAL == rule[0].type:
                if rule[0].nonterminal not in self.go.syntax_info:
                    raise Exception(f"Failed to find '{rule[0].nonterminal}' description in {self.go.syntax_info}")
                self.states.append(
                    WalkStep(
                        state,
                        pos,
                        self.go.syntax_info[rule[0].nonterminal],
                        0,
                        rule[0].nonterminal
                    )
                )
                continue
            if pos >= self.end:
                self.__ret()
                continue
            new_token = self.tokens[pos]
            if NodeType.KEY == rule[0].type and Token.Type.KEY == new_token.token_type and new_token.str == rule[0].str:
                self.states.append(
                    WalkStep(
                        state.parent_state,
                        pos + 1,
                        rule[0],
                        0,
                        state.nonterm
                    )
                )
                continue
            elif NodeType.TERMINAL == rule[0].type and Token.Type.TERMINAL == new_token.type and new_token.terminalType == rule[0].terminal:
                self.states.append(
                    WalkStep(
                        state.parent_state,
                        pos + 1,
                        rule[0],
                        0,
                        state.nonterm
                    )
                )
                continue
            self.__ret()
            continue

    def build(self, go: GrammarObject, tokens: List[Token]) -> ASTNode:
        self.go = go
        self.tokens = tokens
        self.end = len(self.tokens)
        self.axiom = self.go.axiom

        ast = ASTNode(NodeType.NONTERMINAL)
        ast = TreeNode(TreeNode.Type.NONTERMINAL)
        ast.nonterminalType = self.axiom
        ast.childs = []
        ast.commands = []
        nodes_stack = [ast]
        self.__walk()
        for state in self.states:
            pos = state['pos']
            node = state['node']
            rule = node.nextNodes[state['rule_index']]

            if NodeType.END == rule[0].type:
                parent_state = state['parent_state']
                if parent_state is None:
                    if pos == self.end:
                        nodes_stack[-1].commands.append(rule[1])
                        return ast
                    else:
                        raise Exception(f"Fail")
                nodes_stack[-1].commands.append(rule[1])
                nodes_stack.pop()
                continue
            elif NodeType.NONTERMINAL == rule[0].type:
                if rule[0].nonterminal not in self.grammar:
                    raise Exception(f"Failed to find '{rule[0].nonterminal}' description")
                newNonterm = TreeNode(TreeNode.Type.NONTERMINAL)
                newNonterm.nonterminalType = rule[0].nonterminal
                newNonterm.childs = []
                newNonterm.commands = []
                nodes_stack[-1].childs.append(newNonterm)
                nodes_stack[-1].commands.append(rule[1])
                node = rule[0]
                nodes_stack.append(newNonterm)
                continue
            if pos >= self.end:
                raise Exception(f"Fail")
            newToken = self.tokenList[pos]
            if NodeType.KEY == rule[0].type and Token.Type.KEY == newToken.type and newToken.str == rule[0].str:
                element = TreeNode(TreeNode.Type.TOKEN)
                element.attribute = newToken.attribute
                element.token = newToken
                nodes_stack[-1].childs.append(element)
                nodes_stack[-1].commands.append(rule[1])
                continue
            elif NodeType.TERMINAL == rule[0].type and Token.Type.TERMINAL == newToken.type and newToken.terminalType == rule[0].terminal:
                element = TreeNode(TreeNode.Type.TOKEN)
                element.attribute = newToken.attribute
                element.token = newToken
                nodes_stack[-1].childs.append(element)
                nodes_stack[-1].commands.append(rule[1])
                continue

            raise Exception(f"Fail")
        return ast

    def _log(self, message: str):
        """Логирование процесса парсинга"""
        if self._debug:
            print(f"[Parser] {message}")


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