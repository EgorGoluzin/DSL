import re
from DSLTools.models import RuleElement, Rule, ElementType, GrammarToken


# class TreeNode:
#     def __init__(self, name):
#         self.name = name
#         self.children = []
#
#     def add_child(self, child):
#         self.children.append(child)
#
#     def __repr__(self, level=0):
#         ret = "\t" * level + self.name + "\n"
#         for child in self.children:
#             ret += child.__repr__(level + 1)
#         return ret


class Parser:
    def __init__(self, keys_dict: dict[str],
                 nonterminal_dict: dict[str],
                 terminal_dict: dict[str]):
        self.tokens: list[GrammarToken] = None
        self.current_token_index = 0
        self.keys_dict = keys_dict
        self.nonterminal_dict = nonterminal_dict
        self.terminal_dict = terminal_dict

    def tokenize(self, input_text) -> list[GrammarToken]:
        token_pattern = r"""
            (?P<name>[A-Za-z_][A-Za-z0-9_]*)          |  # Имена
            (?P<string>'(\\\\.|[^\\\\'])*')           |  # Строки с экранированием
            (?P<symbol>[:=#;(){}\[\]|.])             |  # Символы
            (?P<whitespace>\s+)                          # Пробельные символы
        """
        tokens = []
        for match in re.finditer(token_pattern, input_text, re.VERBOSE):
            token_type = match.lastgroup
            token_value = match.group(token_type)
            if token_type != "whitespace":
                tokens.append(GrammarToken(value=token_value, token_type=token_type))
        return tokens

    def current_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def consume(self, expected_type=None, expected_value=None):
        token = self.current_token()
        if token is None:
            raise SyntaxError(f"Unexpected end of input at position {self.current_token_index}")
        if (expected_type and token.type != expected_type) or \
                (expected_value and token.value != expected_value):
            raise SyntaxError(
                f"Unexpected token: {token} at position {self.current_token_index}. Expected {expected_value}")
        self.current_token_index += 1
        return token

    def parse_rule(self, rule_name: str, rule_line: str) -> Rule:
        """Метод для парсинга правила. Очевидно основная проблема зключается в правой части!
            Поля:
                rule_name(str): левая часть правила - будет ключем в dict[str, Rule],
                она дублируется в правиле.\n
                rule_line(str): правая часть правила - будет спаршена.
                По ней будет построено дерево? - объект Rule.rpart
        """

        self.tokens = self.tokenize(rule_line)
        self.tokens = self._post_token_process()
        rhs = self._parse_rhs()

        return Rule(lpart=rule_name, rpart=RuleElement(type=ElementType.SEQUENCE, value=[rhs]))

    def _determine_token_attribute_type(self, token_value: str) -> ElementType:
        if token_value in self.keys_dict:
            return ElementType.KEYWORD
        if token_value in self.terminal_dict:
            return ElementType.TERMINAL
        if token_value in self.nonterminal_dict:
            return ElementType.NONTERMINAL
        if token_value == "#":
            return ElementType.SEP_MARKER
        raise ValueError(f"Undefined symbol: {token_value}")

    def _post_token_process(self) -> list[GrammarToken]:
        """Функция для послесканнинга.
            В которой будут вычислены атрибуты лексем (пока это тип для терминальных токенов
             (относительно нашей грамматики)).
        """

        for token in self.tokens:
            if token.type != "symbol":
                token.attribute_type = self._determine_token_attribute_type(token.value)

        return self.tokens

    def _parse_rhs(self) -> RuleElement:
        return self._parse_sequence()

    def _parse_sequence(self, stop_symbols=None) -> RuleElement:
        elements = []
        stop_symbols = stop_symbols or []
        while True:
            current_token = self.current_token()
            if not current_token or current_token.value in stop_symbols:
                break
            element = self._parse_rule_element()
            elements.append(element)
        if not elements:
            raise SyntaxError("Sequence cannot be empty")
        return RuleElement(type=ElementType.SEQUENCE, value=elements)

    def _parse_rule_element(self) -> RuleElement:
        current_token = self.current_token()
        if current_token.value in ('(', '[', '{'):
            if current_token.value == '(':
                element = self._parse_group()
            elif current_token.value == '[':
                element = self._parse_optional()
            else:
                element = self._parse_iteration()
        else:
            element = self._parse_primary_element()

        # Check for alternative
        if self.current_token() and self.current_token().value == '|':
            alternatives = [element]
            while self.current_token() and self.current_token().value == '|':
                self.consume(expected_value='|')
                next_element = self._parse_primary_element_or_structure()
                alternatives.append(next_element)
            return RuleElement(type=ElementType.ALTERNATIVE, value=alternatives)
        return element

    def _parse_primary_element(self) -> RuleElement:
        token = self.current_token()
        if token.type == 'symbol':
            raise SyntaxError(f"Unexpected symbol '{token.value}' at position {self.current_token_index}")
        return RuleElement(type=token.attribute_type, value=token.value)

    def _parse_primary_element_or_structure(self) -> RuleElement:
        current_token = self.current_token()
        if current_token.value in ('(', '[', '{'):
            if current_token.value == '(':
                return self._parse_group()
            elif current_token.value == '[':
                return self._parse_optional()
            else:
                return self._parse_iteration()
        else:
            return self._parse_primary_element()

    def _parse_group(self) -> RuleElement:
        self.consume(expected_value='(')
        sequence = self._parse_sequence(stop_symbols=[')'])
        self.consume(expected_value=')')
        return RuleElement(type=ElementType.GROUP, value=sequence)

    def _parse_optional(self) -> RuleElement:
        self.consume(expected_value='[')
        sequence = self._parse_sequence(stop_symbols=[']'])
        self.consume(expected_value=']')
        return RuleElement(type=ElementType.OPTIONAL, value=sequence)

    def _parse_iteration(self) -> RuleElement:
        self.consume(expected_value='{')
        sequence = self._parse_sequence(stop_symbols=['}', '#'])
        separator = None
        if self.current_token() and self.current_token().value == '#':
            self.consume(expected_value='#')
            name_token = self.current_token()
            if name_token and name_token.type == 'name':
                separator = name_token.value
            else:
                raise SyntaxError("Expected separator name after '#' in iteration")
        self.consume(expected_value='}')
        return RuleElement(type=ElementType.ITERATION, value=sequence, separator=separator)


