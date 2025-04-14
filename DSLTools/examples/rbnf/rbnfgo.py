import os
import pathlib

from DSLTools.core.astgenerator import DefaultAstBuilder
from DSLTools.core.grammar_parsers import RBNFParser
from DSLTools.core.scanning import DefaultScanner
from DSLTools.core.tools import render_tree, get_parser
from DSLTools.core.vertex_tool import generate_wirth_by_rule
from DSLTools.core.wirth_diagram_generation import generate_dot
from DSLTools.models.ast import EvalRegistry, EvalContext
from DSLTools.models.tokens import Tokens, Token
from DSLTools.utils.file_ops import load_config
from DSLTools.utils.wirth_render import render_dot_to_png
from DSLTools.models import GetSyntaxDesription, GrammarObject, Terminal, MetaObject, ASTNode
from settings import settings
from DSLTools.models.legacy_for_wirth import NodeLegacy, NodeTypeLegacy


class RuleAxiomEval(ASTNode.IAttrEval):
    def __call__(self, value, children, context):
        """Правило для аксиомы - Rule"""
        # В нашей грамматике всегда соответствует правой части правила.
        children[0].evaluated(context)
        # В нашей грамматике всегда соответствует Альтернативе(внешней).
        context.current_scope["CURRENT_ENTRY"] = (0, 1)
        context.current_scope["CURRENT_EXIT"] = (0, 1)
        children[2].evaluated(context)
        children[3].evaluated(context)
        return context.current_scope["MATRIX"], \
            context.current_scope["RESULT_VERTEX_LIST"]


class GroupEval(ASTNode.IAttrEval):
    def __call__(self, value, children, context):
        context.current_scope["STACK"].append((
            context.current_scope["CURRENT_ENTRY"],
            context.current_scope["CURRENT_EXIT"]
        ))
        children[0].evaluated(context)
        original_entry, original_exit = context.current_scope["STACK"].pop()
        context.current_scope["CURRENT_ENTRY"] = original_entry
        context.current_scope["CURRENT_EXIT"] = original_exit


class RuleElementEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        if len(children) == 1:
            children[0].evaluated(context)
            return

        return


class OptionalEval(ASTNode.IAttrEval):
    def __call__(self, value, children, context):
        original_entry = context.current_scope["CURRENT_ENTRY"]
        original_exit = context.current_scope["CURRENT_EXIT"]
        new_entry = (original_entry[0] + 1, original_entry[1])
        new_exit = (original_exit[0], original_exit[1] + 1)

        # ε-переходы: вход → новый вход и новый выход → выход
        context.current_scope["MATRIX"][original_entry[0]][new_entry[1]] = 1
        context.current_scope["MATRIX"][new_exit[0]][original_exit[1]] = 1

        # Обработка дочернего элемента
        context.current_scope["CURRENT_ENTRY"] = new_entry
        context.current_scope["CURRENT_EXIT"] = new_exit
        children[0].evaluated(context)


class IterationEval(ASTNode.IAttrEval):
    def __call__(self, value, children, context):
        ## Вопрос совпадают ли всегда при заходе в этот блок CURRENT_ENTRY и CURRENT_EXIT
        entry = context.current_scope["CURRENT_EXIT"]
        # print(entry)
        context.current_scope["CURRENT_ENTRY"] = entry
        # loop_entry = (original_entry[0] + 1, original_entry[1])
        # loop_exit = (original_exit[0], original_exit[1] + 1)
        # Вытаскиваем 2-ой элемент - последовательность!
        children[1].evaluated(context)
        exit_of_it_block = context.current_scope["CURRENT_EXIT"]
        if len(children) != 3:
            # Тут логика - если есть цейтин, то будет и 2 последовательность
            children[3].evaluated(context)
            exit_of_it_block2 = context.current_scope["CURRENT_EXIT"]
            context.current_scope["MATRIX"][exit_of_it_block2[0]][entry[1]] = 1
            context.current_scope["CURRENT_EXIT"] = (exit_of_it_block2[0], exit_of_it_block2[1])
        else:
            # Заполнение обратной связи если нет цейтина.
            context.current_scope["MATRIX"][exit_of_it_block[0]][entry[1]] = 1
        # Обратная связь для повторения
        # context.current_scope["MATRIX"][loop_exit[0]][loop_entry[1]] = 1

        # Обработка разделителя (если есть)



class ElementEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        """Правило для элемента - по-сути это зона перехода
        к вычислению терминальных символов нашей грамматики
        (В пользовательской соответствует - именам терминалов, ключевые слова,
        нетерминалы)."""
        entry = context.current_scope["CURRENT_ENTRY"]
        try:
            context.current_scope["MATRIX"][entry[0]][entry[1]] = 1
            # print(entry)
            # print(children[0].value)
            # print(context.current_scope["MATRIX"])
        except IndexError:
            print("Ouch list index error")
        context.current_scope["CURRENT_EXIT"] = (entry[0] + 1, entry[1] + 1)
        children[0].evaluated(context)


class AlternativeEval(ASTNode.IAttrEval):
    def __call__(self, value, children, context):
        if len(children) == 1:
            children[0].evaluated(context)
            return

        original_entry = context.current_scope["CURRENT_ENTRY"]
        original_exit = context.current_scope["CURRENT_EXIT"]

        new_entry = (original_entry[0] + 1, original_entry[1])
        new_exit = (original_exit[0], original_exit[1] + 1)

        context.current_scope["STACK"].append((original_entry, original_exit))
        for child in children:
            context.current_scope["CURRENT_ENTRY"] = new_entry
            context.current_scope["CURRENT_EXIT"] = new_exit
            child.evaluated(context)
            context.current_scope["MATRIX"][original_entry[0]][new_entry[1]] = 1  # ε-переход
        context.current_scope["CURRENT_ENTRY"], context.current_scope["CURRENT_EXIT"] = context.current_scope[
            "STACK"].pop()


class SequenceEval(ASTNode.IAttrEval):
    def __call__(self, value, children, context):
        entry = context.current_scope["CURRENT_EXIT"]
        for child in children:
            context.current_scope["CURRENT_ENTRY"] = entry
            child.evaluated(context)
            entry = context.current_scope["CURRENT_EXIT"]  # Обновление точки входа
        context.current_scope["CURRENT_ENTRY"] = entry # Финальная точка входа
        # print(entry)
        # print(context.current_scope["CURRENT_ENTRY"])


class KeyWordEval(ASTNode.IAttrEval):
    def __call__(self, value, children, context):
        """Правило для терминала - Ключевого слова в пользовательской грамматике."""
        # Вот тут проверка на то если листочек в массиве ключиков пользователя.
        # Если нас нету то бай бай бай и можем фигачить пустой моковый узел!...
        # TODO: Заменить на нормальные значения узла.
        new_type = None
        new_str = None
        if value in context.symbol_table["USER_KEYWORDS"]:
            new_type = NodeTypeLegacy.KEY
            new_str = value
        else:
            new_type = None
            new_str = None
            context.errors.append(f"Unexpected keyword {children[0]=}")

        new_rule_vertex = NodeLegacy(type=new_type, str_=new_str, nextNodes=[])
        context.current_scope["RESULT_VERTEX_LIST"].append(new_rule_vertex)
        pass


class TerminalOrNonTerminalEval(ASTNode.IAttrEval):
    def __call__(self, value, children, context):
        """Правило для терминала - По своей сути это либо
        имя терминала в пользовательской грамматике, либо
        нетерминал в пользовательской грамматике"""
        # Тут выясняем хто мы?
        # Если нас нету то бай бай бай и можем фигачить пустой моковый узел!...
        # И пишем в ERROR список контекста
        # TODO: Заменить на нормальные значения узла.

        if value in context.symbol_table["USER_TERMINALS_NAME"]:
            new_type = NodeTypeLegacy.TERMINAL
            new_str = value
        elif value in context.symbol_table["USER_NON_TERMINALS"]:
            if context.current_scope["CURRENT_ENTRY"] == (0, 0):
                new_type = NodeTypeLegacy.START
            else:
                new_type = NodeTypeLegacy.NONTERMINAL
            new_str = value
        else:
            new_type = None
            new_str = None
            context.errors.append(f"Unexpected keyword {children[0]=}")

        new_rule_vertex = NodeLegacy(type=new_type, str_=new_str, nextNodes=[])
        context.current_scope["RESULT_VERTEX_LIST"].append(new_rule_vertex)

class EndBlock(ASTNode.IAttrEval):
    def __call__(self, value, children, context):
        """Правило для терминала - По своей сути это либо
        имя терминала в пользовательской грамматике, либо
        нетерминал в пользовательской грамматике"""
        # Тут выясняем хто мы?
        # Если нас нету то бай бай бай и можем фигачить пустой моковый узел!...
        # И пишем в ERROR список контекста
        # TODO: Заменить на нормальные значения узла.

        end_of_rule = NodeLegacy(type=NodeTypeLegacy.END, str_="", nextNodes=[])
        ## Вопрос с расставлением здесь концов.
        last_start_entry = context.current_scope["CURRENT_EXIT"]
        context.current_scope["RESULT_VERTEX_LIST"].append(end_of_rule)
        context.current_scope["MATRIX"][last_start_entry[0]][last_start_entry[1]] = 1

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
end_block = EndBlock()

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
EvalRegistry.register(ASTNode.Type.TOKEN, ';', end_block)
EvalRegistry.register(ASTNode.Type.TOKEN, '.', end_block)

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
counter = 0
for grammar in grammar_names:

    path_to_save_grammar = fr"{directory_to_save}\{grammar}"
    os.makedirs(path_to_save_grammar, exist_ok=True)

    json_path = fr"{directory_to_save_base}\{grammar}\metainfo.json"
    config = load_config(json_path)
    mo_cur = MetaObject(config)
    parser = RBNFParser()
    go_cur: GrammarObject = parser.parse(mo_cur)

    for rule_name, rule_in_cur_grammar in parser.store_for_rules:
        if counter > 0:
            break
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

        con.symbol_table = {"USER_TERMINALS_NAME": go_cur.symbol_table["TERMINALS_NAME_SET"],
                            "USER_NON_TERMINALS": go_cur.symbol_table["NON_TERMINAL_SET"],
                            "USER_KEYWORDS": go_cur.symbol_table["KEYWORD_SET"],
                            "LIST_ROW_TOKENS": terminals}

        rule_matrix = [[0 for _ in range(N)] for _ in range(N)]

        con.current_scope = {
            "MATRIX": rule_matrix,  # Матрица смежности
            "RESULT_VERTEX_LIST": [],  # Список вершин графа
            "STACK": [],  # Магазин для вложенных структур
            "CURRENT_ENTRY": (0, 0),  # Текущая точка входа
            "CURRENT_EXIT": (0, 0),  # Текущая точка выхода

        }


        # with open(fr'{rule_dir}\tokens_{rule_name}.yaml', 'w') as file:
        #     file.write(Tokens(res).to_yaml())

        ast = builder.build(go, res)
        matrix, list_nodes = ast.evaluated(con)
        counter = 1
        wirth_str = generate_wirth_by_rule(list_nodes, matrix)
        with open(fr"{rule_dir}\{rule_name}.gv", 'w') as file:
            file.write(wirth_str)

        render_dot_to_png(pathlib.Path(fr"{rule_dir}\{rule_name}.gv"), pathlib.Path(fr"{rule_dir}"))
        print(matrix)
        print(list_nodes)
        # with open(fr"{rule_dir}\ast_{rule_name}.yaml", 'w') as file:
        #     file.write(ast.to_yaml())

        # render_tree(f"ast_{rule_name}", ast, pathlib.Path(rule_dir))
