# main.py
import sys
import importlib.util
import pathlib
import json
from argparse import ArgumentParser
from DSLTools.models import (MetaObject, TypeParse, IGrammarParser, GrammarObject)
from DSLTools.core.grammar_parsers import RBNFParser
from DSLTools.utils.file_ops import validate_paths

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

#py -m DSLTools.main -j "(ABS/REL)PATHFORMETAOBJ" -d "(ABS/REL)PATHFORDIRTOSAVE(Нужен для запуска но пока ен используется)"
def main():
    # Шаг 1: Парсинг аргументов
    args = parse_arguments()
    json_path = validate_paths(project_path=PROJECT_ROOT, input_path=pathlib.Path(args.jsonFile), is_dir=False)
    directory_to_save = validate_paths(project_path=PROJECT_ROOT, input_path=pathlib.Path(args.directory), is_dir=True)
    # Шаг 2: Загрузка конфигурации
    config = load_config(json_path)
    mo = MetaObject(config)
    # Пример использования
    parser = get_parser(mo)
    # Шаг 3. Парсинг грамматики.
    go = parser.parse(mo)
    # Шаг 4: Генерация dsl_info.py
    generate_dsl_info(go=go, dest=directory_to_save)

    # # Шаг 5: Динамический импорт dsl_info
    # dsl_info = import_dsl_info(args.directory)
    #
    # # Шаг 6: Основной пайплайн обработки
    # process_pipeline(config, dsl_info, args.directory)


# Вспомогательные функции
def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-j", "--json", dest="jsonFile", required=True)
    parser.add_argument("-d", "--dir", dest="directory", required=True)
    return parser.parse_args()


def load_config(json_path):
    with open(json_path) as f:
        return json.load(f)

def get_parser(metadata: MetaObject)->IGrammarParser:
    ## TODO: Заменить на мапу
    if metadata.type_to_parse == TypeParse.RBNF:
        return RBNFParser()

def generate_dsl_info(dest: pathlib.Path, go: GrammarObject):
    from DSLTools.core.dsl_generator import DSLInfoGenerator
    generator = DSLInfoGenerator()
    generator.generate_dsl_info(go=go, dest=dest)


def import_dsl_info(output_dir):
    spec = importlib.util.spec_from_file_location(
        "dsl_info",
        str(pathlib.Path(output_dir) / "dsl_info.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    main()
