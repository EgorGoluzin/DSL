from DSLTools.models.interface import ITokenPostProcessor
from DSLTools.models.tokens import Token
from typing import List, Any
from copy import deepcopy


class ExprEvalMatch(ITokenPostProcessor):
    class NumberEval(Token.IAttrEval):
        def calc(self, value: str) -> Any:
            return int(value)

    class KeyEval(Token.IAttrEval):
        def calc(self, value: str) -> Any:
            return value

    def process(self, tokens: List[Token]) -> List[Token]:
        number_eval = ExprEvalMatch.NumberEval()
        key_eval = ExprEvalMatch.KeyEval()
        retokened = []
        for token in tokens:
            copied = deepcopy(token)
            if Token.Type.TERMINAL == token.token_type:
                copied.eval = number_eval
            elif Token.Type.KEY == token.token_type:
                copied.eval = key_eval
            retokened.append(copied)
        return retokened


class ExprEvalAttrs(ITokenPostProcessor):
    def process(self, tokens: List[Token]) -> List[Token]:
        for token in tokens:
            token.evaluated()
        return tokens
