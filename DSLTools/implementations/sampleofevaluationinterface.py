from dataclasses import dataclass, field
from typing import Callable, Dict, Any, TypeVar, Optional

from enum import Enum


class NodeType(Enum):
    TERMINAL = "terminal"
    NONTERMINAL = "nonterminal"
    KEYWORD = "keyword"


class EvaluationContext:
    def __init__(self):
        self.symbol_table = {}  # Таблица символов
        self.errors = []  # Список ошибок
        self.warnings = []  # Список предупреждений
        self.current_scope = None  # Текущая область видимости
        self.data_types = {}  # Информация о типах данных


# Реестр функций вычисления
class EvaluationRegistry:
    _evaluators: Dict[str, Callable] = {}

    @classmethod
    def register(cls, node_type: str):
        def decorator(func: Callable):
            cls._evaluators[node_type] = func
            return func

        return decorator

    @classmethod
    def get_evaluator(cls, node_type: str) -> Callable:
        return cls._evaluators.get(node_type, lambda value, children, context: None)


TASTNode = TypeVar('TASTNode', bound='ASTNode')


@dataclass
class ASTNode:
    type: NodeType
    subtype: str
    children: list = field(default_factory=list)
    value: str = ''
    attribute: Any = None
    position: Optional[tuple] = None
    evaluation: Optional[Callable[[str, list[TASTNode], EvaluationContext], Any]] = None

    def evaluate(self, context: EvaluationContext):
        # Используем зарегистрированный обработчик или дефолтный
        evaluator = self.evaluation or EvaluationRegistry.get_evaluator(self.subtype)
        try:
            self.attribute = evaluator(self.value, self.children, context)
        except Exception as e:
            context.errors.append(f"Error evaluating {self.subtype} at {self.position}: {str(e)}")
            self.attribute = None

        # Рекурсивное вычисление дочерних узлов
        for child in self.children:
            if isinstance(child, ASTNode):
                child.evaluate(context)

        return self.attribute


# Примеры обработчиков с использованием контекста
@EvaluationRegistry.register("AddExpr")
def add_evaluator(value, children, context):
    left = children[0].attribute if children[0] else 0
    right = children[1].attribute if children[1] else 0

    # Проверка типов
    if not all(isinstance(x, (int, float)) for x in (left, right)):
        context.errors.append(f"Type mismatch in addition at {children[0].position}")
        return None

    return left + right


@EvaluationRegistry.register("Number")
def number_evaluator(value, children, context):
    try:
        return int(value)
    except ValueError:
        context.errors.append(f"Invalid number format: {value}")
        return None