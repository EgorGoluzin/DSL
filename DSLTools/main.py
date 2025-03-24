# main.py
import re
import sys
import pathlib

from DSLTools.core.tools import get_parser
from DSLTools.core.wirth_diagram_generation import generate_dot
from DSLTools.models import (MetaObject, TypeParse, IGrammarParser, GrammarObject)
from DSLTools.utils.file_ops import validate_paths, load_config, generate_file
from DSLTools.core.scanning import DefaultScanner
from DSLTools.core.rule_wirth_converter import convert_rules_to_diagrams
from DSLTools.core.astgenerator import GeneralizedParser
from DSLTools.utils.wirth_render import render_dot_to_png
from settings import settings

PROJECT_ROOT = settings.PROJECT_ROOT

# py -m DSLTools.main -j "(ABS/REL)PATHFORMETAOBJ" -d "(ABS/REL)PATHFORDIRTOSAVE(Нужен для запуска но пока ен используется)"
def main():
    # Шаг 1: Парсинг аргументов
    json_path = fr"{PROJECT_ROOT}\examples\RBNFEXPRESSIONSTESTRULES\metainfo.json"
    directory_to_save = fr"{PROJECT_ROOT}\examples\RBNFEXPRESSIONSTESTRULES"
    # Шаг 2: Загрузка конфигурации
    config = load_config(json_path)
    mo = MetaObject(config)
    # Пример использования
    parser = get_parser(mo)
    # Шаг 3. Парсинг грамматики.
    go = parser.parse(mo)
    diagrams = convert_rules_to_diagrams(go.rules)

    for name, diagram in diagrams.items():
        cur_path = fr"{directory_to_save}\wirthN\{name}.gv"
        generate_file(generate_dot(diagram), pathlib.Path(cur_path))
        render_dot_to_png(cur_path, fr"{directory_to_save}\wirthpngN")

    # Шаг 4: Генерация dsl_info.py
    # generate_dsl_info(go=go, dest=directory_to_save)
    scanner = DefaultScanner(go)
    
    with open(directory_to_save/pathlib.Path("test.smpl")) as f:
        input_str = f.read()
    
    res = scanner.tokenize(input_str)
    print("\n".join([item.__repr__() for item in res]))
    astGen = GeneralizedParser(go)
    ast_head = astGen.parse(res)
    # Шаг 5: Динамический импорт dsl_info
    dsl_info = import_dsl_info(args.directory)
    
    # Шаг 6: Основной пайплайн обработки
    process_pipeline(config, dsl_info, args.directory)





# def process_pipeline(config, dsl_info, output_dir):
#     # Инициализация компонентов с использованием dsl_info
#     from implementations.dsl_scanner import DSLScanner
#     from implementations.dsl_afterscanner import DSLAfterscanner
#
#     scanner = DSLScanner(dsl_info)
#     afterscanner = DSLAfterscanner(dsl_info)
#
#     # Обработка кода
#     with open(config["code"]["path"]) as f:
#         tokens = scanner.tokenize(f.read())
#         processed_tokens = afterscanner.process(tokens)
#
#     # Построение AST
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


if __name__ == "__main__":
    # print(re.findall("Variable", "Variable : Test"))
    main()
