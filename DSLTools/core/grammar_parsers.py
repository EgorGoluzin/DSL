from collections import defaultdict
from typing import Dict, List, Union, Optional, Set, Tuple
from pathlib import Path
import re
from DSLTools.models import (
    Rule, Terminal, GrammarElement, VirtNodeType, GrammarObject,
    IGrammarParser, MetaObject)

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

class ParserError(Exception):
    """Базовый класс для ошибок парсинга RBNF-грамматики."""
    def __init__(self, message: str, line: str = None):
        self.message = message
        self.line = line
        super().__init__(self.message)

class KeyNotMatchedError(ParserError):
    """Ошибка, когда ключ не соответствует ни одному терминалу."""
    def __init__(self, key: str, line: str = None):
        message = f"No one regular form included '{key}'"
        super().__init__(message, line)

class MultipleKeyMatchError(ParserError):
    """Ошибка, когда ключ соответствует нескольким терминалам."""
    def __init__(self, key: str, line: str = None):
        message = f"More than one regular form included '{key}'"
        super().__init__(message, line)

class SeparatorError(ParserError):
    """Ошибка, связанная с некорректным использованием разделителей."""
    def __init__(self, key: str, separator: str, line: str = None):
        message = f"Invalid use of separator '{separator}' in key '{key}'"
        super().__init__(message, line)

class Separators:
    """Класс для управления разделителями в RBNF-парсере."""
    def __init__(self):
        self.separators = {';', '.'}

    def is_separator(self, char: str) -> bool:
        return char in self.separators

class RBNFParser(IGrammarParser):
    def __init__(self):
        self.keys = []
        self.terminals = {}
        self.non_terminals = []
        self.axiom = ""
        self.rules: Dict[str, List[Rule]] = {}  # Изменено на список правил
        self.warnings = []
        self.current_section = None


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
        # Вот эта версия может не работать. В предыдущем коммите еще ок)
        line = line.strip()
        if not line:
            return

        separators = Separators()  # Создаём экземпляр разделителей
        keys = []
        current_key = ""
        in_quotes = False
        quote_char = None

        for char in line:
            if char in ('"', "'") and not in_quotes:  # Начало кавычек
                in_quotes = True
                quote_char = char
                current_key += char
            elif char == quote_char and in_quotes:  # Конец кавычек
                in_quotes = False
                current_key += char
            elif separators.is_separator(char) and not in_quotes:  # Разделитель вне кавычек
                if current_key.strip():
                    keys.append(current_key.strip())
                current_key = ""
            elif char == ' ' and not in_quotes and current_key.strip():  # Пробел вне кавычек
                keys.append(current_key.strip())
                current_key = ""
            else:
                current_key += char

        # Добавляем последний ключ
        if current_key.strip():
            keys.append(current_key.strip())

        # Проверка ключей
        for key in keys:
            if not key:
                continue
            is_key_in_regular_definition_error = True
            is_key_in_more_than_one_regular_def_error = False
            for terminal in self.terminals.values():
                res = re.match(terminal.pattern, key)
                if res is not None and not is_key_in_more_than_one_regular_def_error:
                    self.keys.append((terminal.name, key))
                    is_key_in_regular_definition_error = False
                    is_key_in_more_than_one_regular_def_error = True
                elif is_key_in_more_than_one_regular_def_error and res is not None:
                    raise MultipleKeyMatchError(key, line)
            if is_key_in_regular_definition_error:
                raise KeyNotMatchedError(key, line)

    def _parse_non_terminals(self, line: str):
        nts = [nt.strip() for nt in line.split(';') if nt.strip()]
        self.non_terminals.extend(nts)

    def _parse_axiom(self, line: str):
        self.axiom = line.strip()

    def _parse_rule(self, line: str):
        # Обрабатываем альтернативы вида: A ::= B | C | D
        match = re.match(r'(\w+)\s*::=\s*(.+)', line)
        if not match:
            raise ValueError(f"Invalid rule format: {line}")

        lhs = match.group(1)
        rhs = match.group(2)

        # Разделяем альтернативы
        alternatives = [a.strip() for a in rhs.split('|')]

        rules_for_lhs = []
        for alt in alternatives:
            # Обрабатываем элементы и разделители внутри альтернативы
            if '{' in alt and '}' in alt:
                parts = re.match(r'\s*{(.*?)}(?:\s*#\s*(.*?))?\s*', alt)
                elements = [e.strip() for e in parts.group(1).split() if e.strip()]
                separator = parts.group(2).strip() if parts.group(2) else None
            else:
                elements = [alt.strip()]
                separator = None

            rules_for_lhs.append(Rule(
                lhs=lhs,
                elements=elements,
                separator=separator
            ))

        self.rules[lhs] = rules_for_lhs

    def get_warnings(self) -> List[str]:
        return self.warnings
