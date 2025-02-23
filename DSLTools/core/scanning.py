from abc import ABC, abstractmethod
from typing import List
from ..models.tokens import Token


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