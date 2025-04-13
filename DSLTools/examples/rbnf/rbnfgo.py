import os
import pathlib

from DSLTools.core.astgenerator import DefaultAstBuilder
from DSLTools.core.grammar_parsers import RBNFParser
from DSLTools.core.scanning import DefaultScanner
from DSLTools.core.tools import render_tree, get_parser
from DSLTools.core.wirth_diagram_generation import generate_dot
from DSLTools.models.ast import EvalRegistry, EvalContext
from DSLTools.models.tokens import Tokens, Token
from DSLTools.utils.file_ops import load_config
from DSLTools.utils.wirth_render import render_dot_to_png
from DSLTools.models import GetSyntaxDesription, GrammarObject, Terminal, MetaObject, ASTNode
from settings import settings


class RuleAxiomEval(ASTNode.IAttrEval):
    def __call__(self, value, children, context):
        """Правило для аксиомы - Rule"""
        # В нашей грамматике всегда соответствует правой части правила.
        children[0].evaluated(context)
        # В нашей грамматике всегда соответствует Альтернативе(внешней).
        children[2].evaluated(context)
        return context.current_scope["MATRIX"], \
            context.current_scope["RESULT_VERTEX_LIST"]


class GroupEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        # Группа. Пока не оч ясной какая у нее должна быть семантика с точки зрения графа
        return


class RuleElementEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        return


class OptionalEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        # Ему нужно знать текущую позицию привязки для того чтобы конец связать с началом!
        return


class IterationEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        """ Блок итерации."""
        # Этот парень относительно проблемный. Если в нем есть цейтин - особенно.
        # Ему нужно знать - начало, конец и в случае если есть тот самый, не забыть сделать смещение узла,
        # к которому будет происходить привязка
        pass


class ElementEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        """Правило для элемента - по-сути это зона перехода
        к вычислению терминальных символов нашей грамматики
        (В пользовательской соответствует - именам терминалов, ключевые слова,
        нетерминалы)."""
        return int(value)


class AlternativeEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        """Правило для альтернативы."""
        if len(children) == 1:
            children[0].evaluated(context)
            return

        corent_pos = context.current_scope["CURRENT_MERGE_POSITION"]
        # Вот тут возможно стоит изменять координату на 1
        for el in children:
            el.evaluated(context)

        return value


class SequenceEval(ASTNode.IAttrEval):
    def __call__(self, value, children, context):
        """Правило для последовательности."""
        if len(children) == 1:
            children[0].evaluated(context)
            return

        # Вот тут сто проц меняем координату текущую

        for el in children:
            el.evaluated(context)
        pass


class KeyWordEval(ASTNode.IAttrEval):
    def __call__(self, value, children, context):
        """Правило для терминала - Ключевого слова в пользовательской грамматике."""
        # Вот тут проверка на то если листочек в массиве ключиков пользователя.
        # Если нас нету то бай бай бай и можем фигачить пустой моковый узел!...
        pass


class TerminalOrNonTerminalEval(ASTNode.IAttrEval):
    def __call__(self, value, children, context):
        """Правило для терминала - По своей сути это либо
        имя терминала в пользовательской грамматике, либо
        нетерминал в пользовательской грамматике"""
        # Тут выясняем хто мы?
        # Если нас нету то бай бай бай и можем фигачить пустой моковый узел!...
        # И пишем в ERROR список контекста
        pass


rule_axiom_eval = RuleAxiomEval()

group_eval = GroupEval()
alternative_eval = AlternativeEval()
iteration_eval = IterationEval()
optional_eval = OptionalEval()
rule_elem_eval = RuleElementEval()
sequence_eval = SequenceEval()

element_eval = ElementEval()

users_keyword_eval = KeyWordEval()
users_terminal_or_nonterminal = TerminalOrNonTerminalEval()

EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'Rule', rule_axiom_eval)
EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'Element', element_eval)
EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'Alternative', alternative_eval)
EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'Group', group_eval)
EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'Iteration', iteration_eval)
EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'Optional', optional_eval)
EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'RuleElement', rule_elem_eval)
EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'Sequence', sequence_eval)
EvalRegistry.register(ASTNode.Type.TOKEN, 'name', users_terminal_or_nonterminal)
EvalRegistry.register(ASTNode.Type.TOKEN, 'key_name', users_keyword_eval)

names = ["Alternative", "Element", "Group", "Iteration", "Optional", "Rule", "RuleElement", "Sequence"]
directory_to_save_base = fr"{settings.PROJECT_ROOT}\examples"
directory_to_save = fr"{directory_to_save_base}\rbnf"
# print(GetSyntaxDesription(fr"{directory_to_save}\wirth", None))
# в эту структуру используя матрицу инцидентности и
# Узлы заранее определенные. Пока вполне достаточно использовать GetSyntaxDescription.

OurRules = GetSyntaxDesription(fr"{directory_to_save}\wirth", None)
# for lhs in OurRules:
#     print(f"{lhs=}", f"rhs = {OurRules[lhs]}")

go = GrammarObject(terminals={
    "key_name": Terminal(name="key_name", pattern=r'\'[^\']*\''),
    "name": Terminal(name="name", pattern='[A-Za-z_][A-Za-z0-9_]*'),
    "ebnf_symbol": Terminal(name="ebnf_symbol", pattern="[::=#;(){}\[\]|.]"),
    "whitespace": Terminal(name="whitespace", pattern="\s+")},
    non_terminals=["Alternative", "Element", "Group",
                   "Iteration", "Optional",
                   "Rule", "RuleElement",
                   "Sequence"],
    keys=[("ebnf_symbol", '::='),
          ("ebnf_symbol", ':'),
          ("ebnf_symbol", ';'),
          ("ebnf_symbol", '#'),
          ("ebnf_symbol", '('),
          ("ebnf_symbol", ')'),
          ("ebnf_symbol", '['),
          ("ebnf_symbol", ']'),
          ("ebnf_symbol", '{'),
          ("ebnf_symbol", '}'),
          ("ebnf_symbol", '|'),
          ("ebnf_symbol", '.'),
          ("name", 'RULES')],
    axiom="Rule",
    syntax_info=OurRules)

# grammar_names = ["PSECO", "ISDSL", "GRAPHS", "PUML", "CHAO"]
grammar_names = ["PSECO"]
rule_scanner = DefaultScanner(go)
builder = DefaultAstBuilder(debug=False)
for grammar in grammar_names:

    path_to_save_grammar = fr"{directory_to_save}\{grammar}"
    os.makedirs(path_to_save_grammar, exist_ok=True)

    json_path = fr"{directory_to_save_base}\{grammar}\metainfo.json"
    config = load_config(json_path)
    mo_cur = MetaObject(config)
    parser = RBNFParser()
    go_cur: GrammarObject = parser.parse(mo_cur)

    for rule_name, rule_in_cur_grammar in parser.store_for_rules:
        print(rule_in_cur_grammar)
        rule_dir = fr"{path_to_save_grammar}\ast_{rule_name}"

        os.makedirs(rule_dir, exist_ok=True)
        res = rule_scanner.tokenize(rule_in_cur_grammar)
        terminals = []

        # Здесь вытаскиваем все терминалы - элементы правила.
        for token in res:
            if token.token_type == Token.Type.TERMINAL:
                terminals.append(token)

        # Здесь добавляем вспомогательную 1 для последнего узла.

        N = len(terminals) + 1
        con = EvalContext()

        ## Создаем таблицу символов, которая содержит информацию о
        # пользовательском списке терминалов(именно их имена) / нетерминалов
        # ключевые слова мы отличаем на этапе лексического анализа - они обернуты в ' '

        con.symbol_table = {"USER_TERMINALS_NAME": go_cur.terminals,
                            "USER_NON_TERMINALS": go_cur.non_terminals,
                            "LIST_ROW_TOKENS": terminals}

        rule_matrix = [[0] * N] * N

        con.current_scope = {"MATRIX": rule_matrix,
                             "RESULT_VERTEX_LIST": [],
                             "CURRENT_MERGE_POSITION": (0, 0)}


        # with open(fr'{rule_dir}\tokens_{rule_name}.yaml', 'w') as file:
        #     file.write(Tokens(res).to_yaml())

        ast = builder.build(go, res)

        # with open(fr"{rule_dir}\ast_{rule_name}.yaml", 'w') as file:
        #     file.write(ast.to_yaml())

        # render_tree(f"ast_{rule_name}", ast, pathlib.Path(rule_dir))
