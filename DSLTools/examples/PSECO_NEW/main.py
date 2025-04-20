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
from DSLTools.models.ast import ASTNode, EvalContext, EvalRegistry
from DSLTools.models.tokens import Tokens
from settings import settings
from DSLTools.core.retranslator import ReToExpression
from DSLTools.implementations.token_post_processor import ExprEvalMatch, ExprEvalAttrs
from DSLTools.core.tokenpostprocessing import TokenPostProcessingManager


PROJECT_ROOT = settings.PROJECT_ROOT

EXAMPLE = 21


class ExpressionsEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        context.warnings.append('Calculating Expressions')
        return ('[' +
                ', '.join(
                    str(children[i].evaluated(context))
                    for i in range(0, len(children), 2)
                )
                + ']'
                )


class ExpressionEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        _sum = 0
        for i in range(0, len(children), 2):
            _sum += children[i].evaluated(context)
        return _sum


class TermEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        cum = 1
        for i in range(0, len(children), 2):
            cum *= children[i].evaluated(context)
        return cum


class NumberEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        return int(value)


class KeyEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        return value


class ProgramEval(ASTNode.IAttrEval):
    def __init__(self, name: str):
        self.name = name

    def __call__(self, value, children, context):
        print(f'ProgramEval name: {self.name = }')
        return self.name


class ProgramNameEval(ASTNode.IAttrEval):
    def __call__(self, value, children: list[ASTNode], context):
        return children[0].evaluated(context)


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

EvalRegistry.register(ASTNode.Type.TOKEN, 'number', number_eval)
EvalRegistry.register(ASTNode.Type.TOKEN, '+', key_eval)
EvalRegistry.register(ASTNode.Type.TOKEN, '*', key_eval)
EvalRegistry.register(ASTNode.Type.TOKEN, ',', key_eval)
EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'TERM', term_eval)
EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'EXPRESSION', expression_eval)
EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'EXPRESSIONS', expressions_eval)


# py -m DSLTools.main -j "(ABS/REL)PATHFORMETAOBJ" -d "(ABS/REL)PATHFORDIRTOSAVE(Нужен для запуска но пока ен используется)"
def main():
    # Шаг 1: Парсинг аргументов
    ## Пример с экспрешеном. Просто эти строчки можно закоментить
    # json_path = fr"{PROJECT_ROOT}\examples\expressions\metainfo.json"
    # directory_to_save = fr"{PROJECT_ROOT}\examples\expressions"
    ## Пример с псевдокодом. Просто эти строчки можно раскоментить
    json_path = fr"{PROJECT_ROOT}\examples\PSECO_NEW\metainfo.json"
    directory_to_save = fr"{PROJECT_ROOT}\examples\PSECO_NEW"
    unhappy_files = []
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
    for i in range(6, 6 + 1):
        file_name = f"example{i}"
        # Шаг 4: Генерация dsl_info.py
        # generate_dsl_info(go=go, dest=directory_to_save)
        scanner = DefaultScanner(go)
        # test.smpl
        with open(directory_to_save/pathlib.Path(f"demo_samples/{file_name}.txt")) as f:
            input_str = f.read()
        #
        # input_str = "2 * 5 + 3 + 7, 8, 6 * 1 + 9 * 2"

        res = scanner.tokenize(input_str)
        with open(pathlib.Path(directory_to_save) / 'tokens.yaml', 'w') as file:
            file.write(Tokens(res).to_yaml())
        # afterscanner = TokenPostProcessingManager([
        #     ExprEvalMatch(), ExprEvalAttrs()
        # ])
        #
        # res = afterscanner.execute(res)

        with open(pathlib.Path(directory_to_save) / 'post_token_pseco.yaml', 'w') as file:
            file.write(Tokens(res).to_yaml())

        print("\n".join([item.__repr__() for item in res]))
        builder = DefaultAstBuilder(debug=True)
        try:
            EvalRegistry.register(
                ASTNode.Type.NONTERMINAL, 'Program', ProgramNameEval())
            ast = builder.build(go, res)
            context = EvalContext()
            evaluated = ast.evaluated(context)
            print(f'Result: {evaluated}, {context}')
            with open(directory_to_save/pathlib.Path(f"demo_asts/{file_name}.yaml"), 'w') as file:
                file.write(ast.to_yaml())
            print(f'Finished for {i = }')
        except Exception as e:
            unhappy_files.append({
                'File': file_name,
                'Message': str(e)
            })
    for info in unhappy_files:
        print(f"File: {info['File']}")
        print(f"Message: {info['Message']}")
        print('-' * 20)
    # LD               ::= 'FOR' Expression 'DO' Block 'END_FOR';
    # print(ast)
    # ast = ast.attach_evaluators(evaluators)
    #
    # with open('ast_before.yaml', 'w') as file:
    #     file.write(ast.to_yaml())
    # result = ast.evaluated()
    #
    # with open('ast_after.yaml', 'w') as file:
    #     file.write(ast.to_yaml())
    # print(result)
    #
    # rte = ReToExpression()
    # print(f"Translated output: {rte.translate(ast)}")

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




if __name__ == "__main__":
    # print(re.findall("Variable", "Variable : Test"))
    main()
