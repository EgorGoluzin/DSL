from DSLTools.examples.rbnf.dsl_info import Nonterminal
from DSLTools.models import IRetranslator, ASTNode, NodeType


class ReToExpression(IRetranslator):
    def translate(self, head: ASTNode) -> str | None:
        # Обработка терминалов
        if head.type == NodeType.TERMINAL:
            return head.value

        # Обработка ключей (игнорируем запятые)
        if head.type == NodeType.KEY:
            return head.value if head.value != ',' else None

        # Обработка нетерминалов
        if head.type == NodeType.NONTERMINAL:
            # Рекурсивно обрабатываем дочерние узлы
            children_results = [self.translate(child) for child in head.children if child]
            children_results = [res for res in children_results if res]  # Убираем None

            if head.subtype == Nonterminal.EXPRESSIONS:
                return ",".join(children_results)  # Объединяем выражения через запятую

            elif head.subtype in (Nonterminal.EXPRESSION, Nonterminal.TERM):
                return "".join(children_results)  # Объединяем в одну строку
        return None
