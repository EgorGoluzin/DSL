# main.py
import re
import sys
import pathlib
import time

from DSLTools.core.tools import get_parser
from DSLTools.core.wirth_diagram_generation import generate_dot
from DSLTools.models import (MetaObject, TypeParse, IGrammarParser, GrammarObject)
from DSLTools.utils.file_ops import validate_paths, load_config, generate_file
from DSLTools.core.scanning import DefaultScanner
from DSLTools.core.rule_wirth_converter import convert_rules_to_diagrams
from DSLTools.core.astgenerator import GeneralizedParser, DefaultAstBuilder
from DSLTools.utils.wirth_render import render_dot_to_png
from DSLTools.core.astgenerator import DefaultAstBuilder
from DSLTools.models.ast import ASTNode
from DSLTools.models.tokens import Tokens
from settings import settings
from DSLTools.core.retranslator import ReToExpression

PROJECT_ROOT = settings.PROJECT_ROOT

class ExpressionsEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode]):
        return '[' + ', '.join(str(children[i].evaluated()) for i in range(0, len(children), 2)) + ']'

class ExpressionEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode]):
        _sum = 0
        for i in range(0, len(children), 2):
            _sum += children[i].evaluated()
        return _sum

class TermEval(ASTNode.IAttrEval):
        def __call__(self, value: str, children: list[ASTNode]):
            cum = 1
            for i in range(0, len(children), 2):
                cum *= children[i].evaluated()
            return cum

class NumberEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode]):
        return int(value)

class KeyEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode]):
        return value


expressions_eval = ExpressionsEval()
expression_eval = ExpressionEval()
term_eval = TermEval()
number_eval = NumberEval()
key_eval = KeyEval()

evaluators = {
    (ASTNode.Type.TOKEN, 'number'): number_eval,
    (ASTNode.Type.TOKEN, '+'): key_eval,
    (ASTNode.Type.TOKEN, '*'): key_eval,
    (ASTNode.Type.TOKEN, ','): key_eval,
    (ASTNode.Type.NONTERMINAL, 'TERM'): term_eval,
    (ASTNode.Type.NONTERMINAL, 'EXPRESSION'): expression_eval,
    (ASTNode.Type.NONTERMINAL, 'EXPRESSIONS'): expressions_eval,
}


# py -m DSLTools.main -j "(ABS/REL)PATHFORMETAOBJ" -d "(ABS/REL)PATHFORDIRTOSAVE(Нужен для запуска но пока ен используется)"
def main():
    # Шаг 1: Парсинг аргументов
    ## Пример с экспрешеном. Просто эти строчки можно закоментить
    json_path = fr"{PROJECT_ROOT}\examples\expressions\metainfo.json"
    directory_to_save = fr"{PROJECT_ROOT}\examples\expressions"
    ## Пример с псевдокодом. Просто эти строчки можно раскоментить
    # json_path = fr"{PROJECT_ROOT}\examples\RBNFEXPRESSIONSTESTRULES\metainfo.json"
    # directory_to_save = fr"{PROJECT_ROOT}\examples\RBNFEXPRESSIONSTESTRULES"
    # Шаг 2: Загрузка конфигурации
    config = load_config(json_path)
    # print(config)
    mo = MetaObject(config)
    # Пример использования
    parser = get_parser(mo)
    # Шаг 3. Парсинг грамматики.
    go = parser.parse(mo)
    go.upload(pathlib.Path(fr"{directory_to_save}\wirth"))
    print(go)
    # Шаг 4: Генерация dsl_info.py
    # generate_dsl_info(go=go, dest=directory_to_save)
    scanner = DefaultScanner(go)
    #
    with open(directory_to_save/pathlib.Path("test.smpl")) as f:
        input_str = f.read()
    #

    res = scanner.tokenize(input_str)
    with open('tokens.yaml', 'w') as file:
        file.write(Tokens(res).to_yaml())
    print("\n".join([item.__repr__() for item in res]))
    print(go)
    builder = DefaultAstBuilder()
    ast = builder.build(go, res).attach_evaluators(evaluators)
    with open('ast_before.yaml', 'w') as file:
        file.write(ast.to_yaml())
    result = ast.evaluated()
    
    with open('ast_after.yaml', 'w') as file:
    # with open(f'ast_{time.time_ns()}.yaml', 'w') as file:
        file.write(ast.to_yaml())
    print(result)

    rte = ReToExpression()
    print(f"Translated output: {rte.translate(ast)}")

    #
    # # Шаг 6: Основной пайплайн обработки
    # process_pipeline(config, dsl_info, args.directory)



    # paths = pathlib.Path(pathlib.Path(fr"{directory_to_save}\wirth")).glob('**/*.gv')
    # for cur_path in paths:
    #     render_dot_to_png(cur_path, fr"{directory_to_save}\wirthpngN")

# def process_pipeline(config, dsl_info, output_dir):
#     # Инициализация компонентов с использованием dsl_info
#     from implementations.dsl_scanner import DSLScanner
#     from implementations.dsl_afterscanner import DSLAfterscanner

#     scanner = DSLScanner(dsl_info)
#     afterscanner = DSLAfterscanner(dsl_info)

#     # Обработка кода
#     with open(config["code"]["path"]) as f:
#         tokens = scanner.tokenize(f.read())
#         processed_tokens = afterscanner.process(tokens)
#     print(f'После послесканера:')
#     print(tokens)
# #
# #     # Построение AST
#     from syntax import BuildAst
#     ast = BuildAst(
#         syntax_info=config["syntax"],
#         axiom=dsl_info.axiom,
#         tokens=processed_tokens
#     )
#
#     # Генерация диаграмм
#     from core.dot_generator import DotGenerator
#     DotGenerator(ast).generate(pathlib.Path(output_dir) / "diagrams")

    # diagrams = convert_rules_to_diagrams(go.rules)

    # for name, diagram in diagrams.items():
    #     cur_path = fr"{directory_to_save}\wirthN\{name}.gv"
    #     generate_file(generate_dot(diagram), pathlib.Path(cur_path))
    #     render_dot_to_png(cur_path, fr"{directory_to_save}\wirthpngN")


if __name__ == "__main__":
    # print(re.findall("Variable", "Variable : Test"))
    main()
