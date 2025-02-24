from abc import ABC, abstractmethod
from parse import GrammarObject
from support import MetaObject
from pathlib import Path


class IGrammarParser(ABC):
    @abstractmethod
    def parse(self, meta_info: MetaObject) -> GrammarObject:
        pass


class IGrammarConverter(ABC):
    @abstractmethod
    def convert(self, go: GrammarObject, dest: Path) -> None:
        pass


class IVisualRepresentation(ABC):
    @abstractmethod
    def to_visual(self, dest: Path) -> None:
        pass
