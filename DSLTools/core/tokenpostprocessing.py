from typing import List
from DSLTools.models import ITokenPostProcessor, Token


class TokenPostProcessingManager:
    def __init__(self):
        self._processors: List[ITokenPostProcessor] = []

    def add_processor(self, processor: ITokenPostProcessor):
        self._processors.append(processor)

    def execute(self, tokens: List[Token]) -> List[Token]:
        """Последовательно применяет все обработчики"""
        for processor in self._processors:
            tokens = processor.process(tokens)
        return tokens
