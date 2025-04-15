from typing import List
from DSLTools.models import ITokenPostProcessor, Token


class TokenPostProcessingManager:
    def __init__(self, processors: list[ITokenPostProcessor] = None):
        self.__processors: List[ITokenPostProcessor] = processors or []

    def add_processor(self, processor: ITokenPostProcessor):
        self.__processors.append(processor)

    def execute(self, tokens: List[Token]) -> List[Token]:
        """Последовательно применяет все обработчики"""
        for processor in self.__processors:
            tokens = processor.process(tokens)
        return tokens
