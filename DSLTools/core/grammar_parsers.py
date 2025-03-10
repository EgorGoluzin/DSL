from collections import defaultdict
from typing import Dict, List, Union, Optional, Set, Tuple
from pathlib import Path
import re
from DSLTools.models import (
    Rule, Terminal, GrammarElement, VirtNodeType, GrammarObject,
    IGrammarParser, MetaObject, RuleElement)

PROJECT_ROOT = Path(__file__).parent.parent


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
        self.rules: Dict[str, List[Rule]] = {}  # Изменено на список правил
        self.warnings = []
        self.current_section = None
        self.non_terminals_opt = None
        self.terminals_opt = None
        self.keywords_opt = None


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
                self._parse_rule(line)
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
        alternatives = self._split_alternatives(rhs)

        self.rules[lhs] = [
            Rule(lhs=lhs, elements=self._parse_rhs(alt))
            for alt in alternatives
        ]

    def _split_alternatives(self, rhs: str) -> List[str]:
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        in_quote = False
        split_indices = [0]

        for i, char in enumerate(rhs):
            if char in ('"', "'"):
                in_quote = not in_quote
            elif not in_quote:
                if char in brackets:
                    stack.append(brackets[char])
                elif stack and char == stack[-1]:
                    stack.pop()
                elif not stack and char == '|':
                    split_indices.append(i)

        split_indices.append(len(rhs))
        return [rhs[i:j].strip() for i, j in zip(split_indices, split_indices[1:])]

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
              \# ) | # синтаксическая ]
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

    def _parse_rhs(self, rhs: str) -> List[Dict]:
        tokens = self._tokenize_rhs(rhs)
        elements = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            if token == '{':
                group, i = self._parse_group(tokens, i)
                elements.append(group)
            elif token == '[':
                optional, i = self._parse_optional(tokens, i)
                elements.append(optional)
            else:
                elem_type = self._determine_element_type(token)
                elements.append({'type': elem_type, 'value': token.strip("'")})
                i += 1

        return elements

    def _determine_element_type(self, token: str) -> str:
        if token in self.keywords_opt:
            return 'keyword'
        if token in self.terminals_opt:
            return 'terminal'
        if token in self.non_terminals_opt:
            return 'nonterminal'
        if token.startswith('#') and len(token) > 1:
            return 'separator_marker'
        raise ValueError(f"Undefined symbol: {token}")

    def _parse_group(self, tokens, start_idx):
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
        parsed_elements = self._parse_rhs(' '.join(elements))

        # Обрабатываем сепаратор после группы
        separator = None
        if i < len(tokens) and tokens[i] == '#':
            if i + 1 < len(tokens) and (tokens[i + 1] in self.terminals_opt or tokens[i + 1] in self.keywords_opt):
                separator = tokens[i + 1].strip("'")
                i += 2
            else:
                raise ValueError(f"Invalid separator after group at position {i}")

        return {
            'type': 'group',
            'elements': parsed_elements,
            'separator': separator
        }, i

    def _parse_optional(self, tokens, start_idx):
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

        return {
            'type': 'optional',
            'elements': self._parse_rhs(' '.join(elements))
        }, i
    def get_warnings(self) -> List[str]:
        return self.warnings
