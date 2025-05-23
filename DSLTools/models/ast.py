from dataclasses import dataclass, field
from enum import Enum
from collections.abc import Callable
from typing import Any, TypeVar, NewType
from abc import ABC, abstractmethod
from DSLTools.models.tokens import Token
from DSLTools.models.IYamlMedia import IYamlMedia, YamlString


class NodeType(str, Enum):
    """Тип узла в ПОТОКЕ ТОКЕНОВ. Это не тип узла в АСД, для них используется
    тип ASTNode.Type.
    UPD: кажется, то этот тип нужен для правил, т к если элемент правила
    - Node, то NodeType должен быть типом для правила?..."""
    NONTERMINAL = 'nonterminal'
    TERMINAL = 'terminal'
    KEY = 'key'
    END = 'end'


class TreeNode:
    """Дублирует существующий класс Воротникова, но в предыдущей реализации
    TreeNode содержится класс для типа. Что делает этот класс? Возможно,
    это предыдущая реализация ASTNode?"""
    def __init__(self, node_type, nonterminal_type=None, attribute=None):
        self.type = node_type
        self.nonterminal_type = nonterminal_type
        self.attribute = attribute
        self.childs = []


TASTNode = TypeVar('TASTNode', bound='ASTNode')


@dataclass
class EvalContext:
    symbol_table: dict = field(default_factory=dict)
    errors:       list = field(default_factory=list)
    warnings:     list = field(default_factory=list)
    current_scope: Any = None
    data_types:   dict = field(default_factory=dict)


class IASTNode(ABC):
    """Элемент абстрактного синтаксического дерева."""
    @abstractmethod
    def evaluated(self, context: EvalContext) -> Any:
        pass


JsonString = NewType('JsonString', str)


class IJsonMedia(ABC):
    """Объект, преобразуемый в формат JSON."""
    @abstractmethod
    def to_json(self, offset: int = 0) -> JsonString:
        pass


@dataclass
class ASTNode(IASTNode, IJsonMedia, IYamlMedia):
    """Узел абстрактного синтаксического дерева."""
    class IAttrEval(ABC):
        """Интерфейс для класса, считающего значение атрибута в узле АСД."""
        @abstractmethod
        def __call__(
            self,
            value: str,
            children: list[TASTNode],
            context: EvalContext
        ) -> Any:
            pass

    class IdentityEval(IAttrEval):
        """Базовая реализация тождественного вычислителя атрибутов."""
        def __call__(
            self,
            value: str,
            children: list[TASTNode],
            context: EvalContext
        ) -> Any:
            return value

    class Type(str, Enum):
        """Тип узла АСД. Бинарная классификация узлов на токены и нетерминалы
        унаследована от алгоритма псевдокода прошлого года. Почему именно
        токен - неизвестно. Тип поля type оставлен как NodeType | Type для
        обратной совместимости. Вообще говоря, тут должен быть только Type,
        т. к. NodeType относится к токенам. Причина путаницы - у Воротникова
        и псевдокода прошлого года Node обозначало не узел дерева, а элемент
        правил."""
        TOKEN = 'TOKEN'
        NONTERMINAL = 'NONTERMINAL'
    type: Type
    """Тип узла: терминал-нетерминал-ключ"""
    subtype: 'str' = ''
    """Подтип нетерминала или терминала - используемые в вашем коде"""
    children: list[TASTNode] = field(default_factory=list)
    """Дочерние узлы"""
    nonterminalType: str = ''
    """Неизвестное на данный момент поле. Прописано явно для улучшения
    читаемости"""
    commands: list = field(default_factory=list)
    """Неизвестное на данный момент поле. Прописано явно для улучшения
    читаемости"""
    token: Token = None
    """Токен, сохраняемый в элементе дерева. Появилось в результате
    переписывания алгоритма псевдокода предыдущего года."""
    value: str = ''
    """Значение (для терминалов)"""
    attribute: Any = None
    """Вычисляемый атрибут. Для терминалов - после послесканера, для
    нетерминалов - при обсчете дерева."""
    position: tuple = None
    """(line, column)"""
    evaluation: IAttrEval = IdentityEval()
    """собственное значение, список значений дочерних узлов,
    # возвращаемый тип (любой)"""
    SHIFT = 4

    def __blank(self, offset: int):
        return ' ' * self.SHIFT * offset

    def evaluated(self, context: EvalContext) -> Any:
        # self.attribute = self.evaluation(self.value, self.children)
        evaluation = EvalRegistry.evaluation(self.type, self.subtype)
        self.attribute = evaluation(self.value, self.children, context)
        return self.attribute

    def attach_evaluators(
        self, evals: dict[tuple[Type, str], IAttrEval]
    ) -> TASTNode:
        key = (self.type, self.subtype)
        # print(f'{key = }, {key in evals}, {evals = }')
        if key in evals:
            # print(f'Found {key}')
            self.evaluation = evals[key]
        for child in self.children:
            child.attach_evaluators(evals)
        return self

    def json_no_newline(self, offset: int):
        json = (
            self.__blank(offset) + '{\n'
            + self.__blank(offset + 1) + f"type: '{self.type}',\n"
            + self.__blank(offset + 1) + f"subtype: '{self.subtype}',\n"
            + self.__blank(offset + 1) + f"value: '{self.value}',\n"
            + self.__blank(offset + 1) + f"attribute: '{'' if self.attribute is None else self.attribute}',\n"
            + self.__blank(offset + 1) + 'children: ['
        )
        if self.children == []:
            json += ']\n' + self.__blank(offset) + '}'
        else:
            json += '\n'
            for child in self.children[:-1]:
                json += child.json_no_newline(offset + 2) + ',\n'
            json += self.children[-1].json_no_newline(offset + 2) + '\n'
            json += self.__blank(offset + 1) + ']\n' + self.__blank(offset) + '}'
        return json

    def to_json(self, offset: int = 0) -> JsonString:
        return self.json_no_newline(offset) + '\n'

    def to_yaml(self, offset: int = 0) -> YamlString:
        blank = self.__blank(offset)
        yaml = (
            blank + f"type: '{self.type}'\n"
            + blank + f"subtype: '{self.subtype}'\n"
            + blank + f"value: '{self.value}'\n"
            + blank + f"attribute: '{'' if self.attribute is None else self.attribute}'\n"
            + blank + 'children:'
        )
        if offset != 0:
            listed = list(yaml)
            listed[len(blank) - 2] = '-'
            yaml = ''.join(listed)
        if self.children == []:
            yaml += ' []\n'
        else:
            yaml += '\n'
            for child in self.children:
                yaml += child.to_yaml(offset + 1)
        return yaml


class EvalRegistry:
    _evaluators: dict[tuple[ASTNode.Type, str], ASTNode.IAttrEval] = {}

    @classmethod
    def register(
        cls, type: ASTNode.Type, subtype: str, evaluation: ASTNode.IAttrEval
    ):
        cls._evaluators[(type, subtype)] = evaluation

    @classmethod
    def evaluation(cls, type: ASTNode.Type, subtype: str) -> ASTNode.IAttrEval:
        return cls._evaluators.get((type, subtype), ASTNode.IdentityEval())

    @classmethod
    def clear(cls) -> None:
        cls._evaluators = {}
