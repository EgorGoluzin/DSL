from abc import ABC, abstractmethod
from parse import GrammarObject
from support import MetaObject


class IGrammarParser(ABC):
    @abstractmethod
    def parse(self, meta_info: MetaObject) -> GrammarObject:
        pass
