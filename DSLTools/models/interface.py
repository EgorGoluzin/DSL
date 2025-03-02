from abc import ABC, abstractmethod
from .parse import GrammarObject
from .support import MetaObject
from .tokens import Token
from pathlib import Path
from typing import List


class IGrammarParser(ABC):
    """Используется в парсерах грамматики при различных форматах задания."""

    @abstractmethod
    def parse(self, meta_info: MetaObject) -> GrammarObject:
        pass


class IGrammarConverter(ABC):
    """Используется в конвертерах из GrammarObject -> грамматику в определенном формате задания."""

    @abstractmethod
    def convert(self, go: GrammarObject, dest: Path) -> None:
        pass


class IVisualRepresentation(ABC):
    """Используется в конвертерах (для визуализации полученного файла)
    из GrammarObject -> грамматику в определенном формате задания."""

    @abstractmethod
    def to_visual(self, dest: Path) -> None:
        pass


class IScanner(ABC):
    """Абстрактный интерфейс для сканера"""

    @abstractmethod
    def tokenize(self, code: str) -> List[Token]:
        pass


class IAfterscanner(ABC):
    """Абстрактный интерфейс для постобработки токенов"""

    @abstractmethod
    def process(self, tokens: List[Token]) -> List[Token]:
        pass
