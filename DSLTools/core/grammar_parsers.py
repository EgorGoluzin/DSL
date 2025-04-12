from collections import defaultdict
from typing import Dict, List, Union, Optional, Set, Tuple
from pathlib import Path
import re
from DSLTools.models import (
    Rule, Terminal, GrammarElement, VirtNodeType, GrammarObject,
    IGrammarParser, MetaObject, RuleElement, ElementType)

PROJECT_ROOT = Path(__file__).parent.parent


class Tokenizer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def peek(self):
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return None

    def consume(self):
        if self.index < len(self.tokens):
            token = self.tokens[self.index]
            self.index += 1
            return token
        return None


class VirtParser(IGrammarParser):
    def __init__(self):
        self.rules: Dict[str, List[Rule]] = {}
        self.edges: Dict[str, List[Tuple[str, Optional[Terminal]]]] = defaultdict(list)
        self.node_map: Dict[str, Union[GrammarElement, VirtNodeType]] = {}

    def parse(self, model_info: MetaObject) -> GrammarObject:
        syntax_dir = model_info.syntax["info"]["syntax_dir"]
        support_file = model_info.syntax["info"]["support_file"]
        rules_of_grammar = self._syntax_parse(syntax_dir)
        terminals, non_terminals, axiom = self._support_parse(support_file)
        return GrammarObject(rules=rules_of_grammar, terminals=terminals,
                             non_terminals=non_terminals, axiom=axiom)

    def _syntax_parse(self, diagrams_dir: Path):
        """"""
        for dot_file in diagrams_dir.glob("*.gv"):
            self._process_diagram(dot_file)
        return

    def _support_parse(self, support_file: Path):
        """Даем путь к sgi файлу с инфой по лексике и вызываем функцию для ее парсинга"""
        return [""], [""], ""

    def _process_diagram(self, dot_file):
        """"""
        pass


class UMLParser(IGrammarParser):
    def parse(self, meta_object: MetaObject) -> GrammarObject:
        syntax_dir = meta_object.syntax["info"]["syntax_dir"]
        support_file = meta_object.syntax["info"]["support_file"]
        rules_of_grammar = self._syntax_parse(syntax_dir)
        terminals, non_terminals, axiom = self._support_parse(support_file)
        return GrammarObject(rules=rules_of_grammar, terminals=terminals,
                             non_terminals=non_terminals, axiom=axiom)

    def _syntax_parse(self, syntax_dir) -> Dict[str, List[str]]:
        return {"default": [""]}

    def _support_parse(self, support_file: Path):
        return [""], [""], ""


class RBNFParser(IGrammarParser):
    def __init__(self):
        self.keys = []
        self.terminals = {}
        self.non_terminals = []
        self.axiom = ""
        self.rules: Dict[str, Rule] = {}  # Изменено на список правил
        self.warnings = []
        self.current_section = None
        self.non_terminals_opt = None
        self.terminals_opt = None
        self.keywords_opt = None
        self.store_for_rules = []

    def parse(self, meta_object: MetaObject) -> GrammarObject:
        syntax_dir = meta_object.syntax["info"]["syntax_dir"]
        syntax_path = rf"{PROJECT_ROOT}\{syntax_dir}\{meta_object.syntax['info']['filenames'][0]}"
        self._syntax_parse(syntax_path)
        return GrammarObject(keys=self.keys,
                             terminals=self.terminals,
                             non_terminals=self.non_terminals,
                             axiom=self.axiom, rules=self.rules)

    def _syntax_parse(self, syntax_dir):
        with open(syntax_dir, "r") as r:
            content = r.read()
            self._parse_iner(content)

    def _parse_iner(self, content: str):
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.strip().rstrip(';.')
            if not line or line.startswith('#'):
                continue
            # Detect section headers
            if line.endswith(':'):
                self.current_section = line[:-1].upper()
                continue
            self._parse_line(line, line_num)

    def _parse_line(self, line: str, line_num: int):
        try:
            if self.current_section == 'TERMINALS':
                self._parse_terminal(line)
            elif self.current_section == 'KEYS':
                self._parse_keys(line)
            elif self.current_section == 'NONTERMINALS':
                self._parse_non_terminals(line)
            elif self.current_section == 'AXIOM':
                self._parse_axiom(line)
            elif self.current_section == 'RULES':
                # self._parse_rule(line)
                self._save_rule_line(line)
        except Exception as e:
            self.warnings.append(f"Line {line_num}: Error parsing '{line}' - {str(e)}")

    def _parse_terminal(self, line: str):
        match = re.match(r'(\w+)\s*::=\s*(\'.*?\'|".*?")', line)
        if not match:
            raise ValueError(f"Invalid terminal format: {line}")

        name = match.group(1)
        pattern = match.group(2).strip('\'"')
        self.terminals[name] = Terminal(name, pattern)

    def _parse_keys(self, line: str):
        if line == ";":
            key = line
            for terminal in self.terminals.values():
                res = re.match(terminal.pattern, key)
                if res is not None:
                    self.keys.append((terminal.name, key))
                    return
        keys = [k.strip('\'" ') for k in line.split(' ') if k.strip()]
        is_key_in_regular_definition_error = True
        is_key_in_more_than_one_regular_def_error = False
        for key in keys:
            for terminal in self.terminals.values():
                res = re.match(terminal.pattern, key)
                if res is not None and not is_key_in_more_than_one_regular_def_error:
                    self.keys.append((terminal.name, key))
                    is_key_in_regular_definition_error = False
                    is_key_in_more_than_one_regular_def_error = True
                elif is_key_in_more_than_one_regular_def_error and res is not None:
                    raise f"More than one regular form included {key}"
            if is_key_in_regular_definition_error:
                raise f"No one regular form included {key}"

    def _parse_non_terminals(self, line: str):
        nts = [nt.strip() for nt in line.split(';') if nt.strip()]
        self.non_terminals.extend(nts)

    def _parse_axiom(self, line: str):
        self.axiom = line.strip()

    def _save_rule_line(self, line: str):
        match = re.match(r'(\w+)\s*::=\s*(.+)', line)
        lhs = match.group(1)
        self.store_for_rules.append((lhs, f"{line};"))
    def _parse_rule(self, line: str):
        # Извлекаем LHS и RHS

        if self.non_terminals_opt is None:
            self.non_terminals_opt = set(self.non_terminals)
            self.terminals_opt = set(self.terminals.keys())
            self.keywords_opt = {f"'{k[1]}'" for k in self.keys}

        match = re.match(r'(\w+)\s*::=\s*(.+)', line)
        if not match:
            raise ValueError(f"Invalid rule format: {line}")

        lhs = match.group(1)
        if lhs not in self.non_terminals:
            raise ValueError(f"Undefined non-terminal in LHS: {lhs}")

        rhs = match.group(2).strip().rstrip(';')
        self.rules[lhs] = Rule(lpart=lhs, rpart=RuleElement(type=ElementType.SEQUENCE,
                                                            value=self._parse_rhs(rhs)))

    def _tokenize_rhs(self, rhs: str) -> List[str]:
        # Регулярка разделяет:
        # 1. Строковые литералы (в кавычках)
        # 2. Синтаксические скобки EBNF
        # 3. Идентификаторы (терминалы/нетерминалы)
        tokens = re.findall(
            r"""
            ( '.*?'      |   # строки в одинарных кавычках
              ".*?"      ) | # строки в двойных кавычках
            ( \{         |   # синтаксическая {
              \}         |   # синтаксическая }
              \[         |   # синтаксическая [
              \]         |
              \#         |
              \|) | # синтаксическая ]
            ( \w+        )   # слова (терминалы/нетерминалы)
            """,
            rhs,
            flags=re.VERBOSE
        )

        # Объединяем результаты групп и фильтруем пустые
        return [
            t[0] or t[1] or t[2]
            for t in tokens
            if any(t)
        ]

    def _parse_rhs(self, rhs: str) -> List[RuleElement]:
        """
        Функция для обработки правила, она как раз таки является рекурсивной.
        В ней происходит обработка всех случаев: Optional | Group | Alternative.
        """
        tokens = self._tokenize_rhs(rhs)
        elements = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == '{':
                group, i = self._parse_group(tokens, i)
                elements.append(group)
                continue
            elif token == '[':
                optional, i = self._parse_optional(tokens, i)
                elements.append(optional)
                continue
            elif len(tokens) > i+1:
                if tokens[i+1] == '|':
                    alternative, i = self._parse_alternative(tokens, i)
                    elements.append(alternative)
                    continue
                if token == '|':
                    alternative, i = self._parse_alternative(tokens, i)
                    elements.append(alternative)
                    continue

            if token:
                elem_type = self._determine_element_type(token)
                elements.append(RuleElement(type=elem_type, value=token.strip("'")))
                i += 1

        return elements

    def _parse_alternative(self, tokens, start_index) -> (RuleElement, int):
        alternatives = []
        i = start_index
        depth = 0  # Для отслеживания вложенности скобок

        while True:
            current_alt_tokens = []
            # Собираем токены текущей альтернативы, учитывая вложенность
            while i < len(tokens):
                token = tokens[i]
                if token == '|' and depth == 0:
                    i += 1  # Пропускаем '|' для следующей альтернативы
                    break
                # Обновляем глубину вложенности
                if token in ['{', '[', '(']:
                    depth += 1
                elif token in ['}', ']', ')']:
                    depth -= 1
                current_alt_tokens.append(token)
                i += 1

            # Парсим собранные токены в последовательность элементов
            if current_alt_tokens:
                rhs = ' '.join(current_alt_tokens)
                parsed_elements = self._parse_rhs(rhs)
                # Каждая альтернатива — это последовательность (SEQUENCE)
                if len(parsed_elements) > 1:
                    alt_element = RuleElement(
                        type=ElementType.SEQUENCE,
                        value=parsed_elements
                    )
                else:
                    alt_element = parsed_elements[0]
                alternatives.append(alt_element)

            # Выходим, если больше нет альтернатив
            if i >= len(tokens) or (len(current_alt_tokens) == 0 and tokens[i - 1] != '|'):
                break

        return RuleElement(type=ElementType.ALTERNATIVE, value=alternatives), i

    def _parse_group(self, tokens, start_idx) -> (RuleElement, int):
        """Функция для парсинга случая групп"""
        elements = []
        i = start_idx + 1
        depth = 1

        # Собираем элементы внутри группы
        while i < len(tokens):
            token = tokens[i]
            if token == '{':
                depth += 1
            elif token == '}':
                depth -= 1
                if depth == 0:
                    i += 1  # Пропускаем '}'
                    break
            elements.append(token)
            i += 1

        # Парсим содержимое группы
        separator = None
        parsed_elements = self._parse_rhs(' '.join(elements))
        for j, el in enumerate(parsed_elements):
            if el.type == ElementType.SEP_MARKER:
                separator = parsed_elements[j+1]
                parsed_elements.pop(j+1)
                parsed_elements.pop(j)
                # TODO: продумать здесь кринж логику
                break
        # Обрабатываем сепаратор после группы

        return RuleElement(
            type=ElementType.GROUP,
            value=parsed_elements,
            separator=separator), i

    def _parse_optional(self, tokens, start_idx) -> (RuleElement, int):
        """Функция для парсинга случая опциональных моментов"""
        elements = []
        i = start_idx + 1
        depth = 1

        while i < len(tokens):
            token = tokens[i]
            if token == '[':
                depth += 1
            elif token == ']':
                depth -= 1
                if depth == 0:
                    i += 1  # Пропускаем ']'
                    break
            elements.append(token)
            i += 1

        return RuleElement(type=ElementType.OPTIONAL, value=self._parse_rhs(' '.join(elements))), i

    def _determine_element_type(self, token: str) -> ElementType:
        if token in self.keywords_opt:
            return ElementType.KEYWORD
        if token in self.terminals_opt:
            return ElementType.TERMINAL
        if token in self.non_terminals_opt:
            return ElementType.NONTERMINAL
        if token == "#":
            return ElementType.SEP_MARKER
        raise ValueError(f"Undefined symbol: {token}")

    def get_warnings(self) -> List[str]:
        return self.warnings
