import re
from typing import List

from _elementtree import ParseError

from DSLTools.models import (GrammarObject, Token, ASTNode, Rule, IAstBuilder, IAstRender)


class DefaultAstBuilder(IAstBuilder):

    def build(self, go: GrammarObject, tokens: List[Token]) -> ASTNode:
        pass

    def _log(self, message: str):
        """Логирование процесса парсинга"""
        if self._debug:
            print(f"[Parser] {message}")

class DefaultAstRenderer(IAstRender):
    def build(self, go: GrammarObject, tokens: List[Token]) -> ASTNode:
        pass



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
