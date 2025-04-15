from DSLTools.examples.rbnf.dsl_info import Nonterminal
from DSLTools.models import IRetranslator, ASTNode, NodeType


class ReToExpression(IRetranslator):
    def translate(self, head: ASTNode) -> str | None:
        # Обработка терминалов
        if head.type == ASTNode.Type.TOKEN:
            # Возвращаем значение, если оно не является запятой
            return head.value if head.value != ',' else None

        # Обработка нетерминалов
        if head.type == ASTNode.Type.NONTERMINAL:
            # Рекурсивно обрабатываем дочерние узлы, исключая None
            children_results = [
                res for child in head.children if child
                if (res := self.translate(child)) is not None
            ]

            # Словарь для объединения результатов в зависимости от подтипа
            join_strategies = {
                Nonterminal.EXPRESSIONS: lambda results: ",".join(results),
                Nonterminal.EXPRESSION: lambda results: "".join(results),
                Nonterminal.TERM: lambda results: "".join(results),
            }

            # Выбираем стратегию объединения или возвращаем None
            strategy = join_strategies.get(head.subtype)
            return strategy(children_results) if strategy else None

        # Если тип узла не распознан, возвращаем None
        return None
