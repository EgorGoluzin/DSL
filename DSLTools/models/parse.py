from typing import List, Optional, Dict, Tuple, Union, Any
from enum import Enum
from dataclasses import dataclass, field


class VirtNodeType(Enum):
    NONTERMINAL = "box"
    TERMINAL = "diamond"
    KEYWORD = "oval"
    START = "plaintext"
    END = "point"


class GrammarElement:
    pass


@dataclass
class Terminal:
    name: str
    pattern: str

    def __str__(self) -> str:
        return f"Terminal(name: {self.name}, pattern: {self.pattern})"


class ElementType(Enum):
    KEYWORD = "keyword"
    NONTERMINAL = "nonterminal"
    TERMINAL = "terminal"
    GROUP = "group"
    OPTIONAL = "optional"
    ALTERNATIVE = "alternative"
    SEQUENCE = "sequence"
    SEPARATOR = "separator"
    MODIFIER = "modifier"
    SEP_MARKER = "sep_marker"
    MERGE_FLAG = "merge_flag"
    ALTERNATIVE_FLAG = "alternative_flag"


@dataclass
class RuleElement:
    """Класс для представления элементов правил грамматики в EBNF-формате.

    Поля:
        type (ElementType): Тип элемента (группа, альтернатива, терминал и т.д.).\n
        value (Union[str, List[RuleElement]]):
            - Для элементарных типов (KEYWORD, NONTERMINAL, TERMINAL) — строковое значение.
            - Для составных типов (GROUP, ALTERNATIVE, SEQUENCE) — список вложенных элементов.
        modifier (str): Модификатор повторяемости(пока не используются):
            - "" — отсутствует,
            - "*" — 0 или более повторений,
            - "+" — 1 или более повторений,
            - "?" — опциональное вхождение (0 или 1 раз).

        separator (Optional[RuleElement]): Сепаратор для групп с повторениями.
            Пример:
            Правило `Arguments ::= { Expression # "," }` будет иметь:
            - type=GROUP,
            - value=[RuleElement(value=Expression, type=ElementType.NONTERMINAL, separator=None)],
            - separator=RuleElement(type=KEYWORD, value=",").

    Примеры использования:
        1. Терминал:
            RuleElement(type=ElementType.TERMINAL, value="name")
        2. Группа с сепаратором "','":
            RuleElement(
                type=ElementType.GROUP,
                value=[...],
                separator=RuleElement(type=ElementType.KEYWORD, value="','")
            )
        3. Опциональный элемент:
            RuleElement(
                type=ElementType.OPTIONAL,
                value=[...],
            )
    """
    type: ElementType
    value: Union[str, List['RuleElement']]  #
    modifier: str = ""  # "*", "+", "?" для повторений и опционалов
    separator: Optional['RuleElement'] = None  # Для групп с сепаратором

    def __str__(self):
        base = self._format_base("")
        return f"{base}{self.modifier}" if self.modifier else base

    def _format_base(self, sep: str) -> str:
        if self.type == ElementType.ALTERNATIVE:
            return f"({' | '.join(str(e) for e in self.value)})"
        if self.type == ElementType.GROUP:
            inner = f"{self.separator} ".join(str(e) for e in self.value)
            return f"({inner})"
        if self.type == ElementType.OPTIONAL:
            return f"[{''.join(str(e) for e in self.value)}]"
        return f'"{self.value}"' if self.type == ElementType.KEYWORD else self.value

    def _format_base_with_sep(self, sep: str) -> str:
        if self.type == ElementType.ALTERNATIVE:
            ch = ' | '
            return f"Alter( {sep} {ch.join([e.to_string(sep) for e in self.value])})"
        if self.type == ElementType.GROUP:
            ch = sep + str(self.separator)
            inner = sep + ch.join([e.to_string(sep) for e in self.value])
            return f"({inner})"
        if self.type == ElementType.OPTIONAL:
            return sep + f"Optional[{f'{sep}'.join([e.to_string(sep) for e in self.value])}]"
        if self.type == ElementType.SEQUENCE:
            ch = sep
            inner = sep + ch.join([e.to_string(sep) for e in self.value])
            return f"{sep}Seq ({inner})"
        return f'"Key(value={self.value})"' if self.type == ElementType.KEYWORD else f"Nonterminal(value = {self.value})"

    def to_string(self, sep: str) -> str:
        sep += "\t"
        base = self._format_base_with_sep(sep)
        return f"{base}{self.modifier}" if self.modifier else base


@dataclass
class Rule:
    """Класс правила, который оборачивает прям все правило.

    Поля:
        lpart(str): Левая часть правила.\n
        rpart(RuleElement): Правая часть.
            - Важно что она сейчас обернута в RuleElement(type=ElementType.SEQUENCE, value=[...], separator=None)
            при этом, этот тип больше пока нигде не используется.
    """

    lpart: str
    rpart: RuleElement  # Основное изменение: список альтернатив

    def __str__(self):
        return f"{self.lpart} ::= \n" + str(self.rpart)

    def to_string(self, sep) -> str:
        return f"{self.lpart} ::=" + self.rpart.to_string(sep)
    # def __str__(self):
    #     return f"Rule( lhs = {self.lhs}, elements: " + "\n\t".join([el.__str__() for el in self.elements])\
    #         + f"\n\tsep={self.separator})"


@dataclass
class GrammarObject:
    """Замена dsl_info + блока правил. Этот объект ключевой в задании dsl он
    используется для задания пользовательской грамматики,
    по-сути являясь ее представлением во всей программе."""

    terminals: Dict[str, Terminal] = field(default_factory=dict)
    keys: List[Tuple[str, str]] = field(default_factory=list)
    non_terminals: List[str] = field(default_factory=list)
    axiom: str = ''
    rules: Dict[str, Rule] = field(default_factory=dict)
    syntax_info: dict = None

    def __post_init__(self):
        self._validate()

    def _validate(self):
        pass
        # Проверка аксиомы
        # if self.axiom not in self.non_terminals:
        #     raise ValueError(f"Axiom '{self.axiom}' is not a defined non-terminal")
        #
        # # Проверка правил
        # for nt, rule in self.rules.items():
        #     if nt not in self.non_terminals:
        #         raise ValueError(f"Undefined non-terminal in rule: {nt}")

        # Проверка уникальности терминалов и ключей
        # all_symbols = [t.name for t in self.terminals.values()] + [k[0] for k in self.keys]
        # if len(all_symbols) != len(set(all_symbols)):
        #     raise ValueError("Duplicate terminal/key definitions")

    def get_terminals_for_template(self) -> str:
        return "\n\t" + "\n\t".join([f"{item} = '{item}'" for item in self.terminals.keys()])

    def get_regular_expression_for_template(self):
        return ",\n\t".join([f"(Terminal.{item.name}, r'{item.pattern}')" for item in self.terminals.values()])

    def get_keys_for_template(self):
        return ",\n\t".join([f"('{item[1]}', Terminal.{item[0]})" for item in self.keys])

    def get_non_terminals_for_template(self):
        return "\n\t" + "\n\t".join([f"{item} = '{item}'" for item in self.non_terminals])

    def __str__(self):
        res = "GrammarObject(\n\tTerminals:"
        res += "\n\t\t" + "\n\t\t".join([item.__str__() for item in self.terminals.values()]) + ";"
        ## TODO: Создать класс для ключей
        res += "\n\tKeys:" + "\n\t\t" + "\n\t\t".join([f"type: {item[0]}, val: {item[1]}" for item in self.keys]) + ";"
        res += "\n\tNonTerminals:" + "\n\t\t" + "\n\t\t".join(self.non_terminals) + ";"
        res += "\n\tRules:" + "\n\t\t" + "\n\t\t".join([rule.to_string("\n\t\t") for rule in self.rules.values()])
        res += "\n\tAxiom:" + f"\n\t\t{self.axiom}"
        return res
