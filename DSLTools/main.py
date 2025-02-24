# main.py
import importlib.util
import pathlib
import json
from argparse import ArgumentParser


def main():
    # Шаг 1: Парсинг аргументов
    args = parse_arguments()

    # Шаг 2: Загрузка конфигурации
    config = load_config(args.jsonFile)

    # Шаг 3: Извлечение метаданных грамматики
    metadata = extract_metadata(config)

    # Шаг 4: Генерация dsl_info.py
    generate_dsl_info(metadata, args.directory)

    # Шаг 5: Динамический импорт dsl_info
    dsl_info = import_dsl_info(args.directory)

    # Шаг 6: Основной пайплайн обработки
    process_pipeline(config, dsl_info, args.directory)


# Вспомогательные функции
def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-j", "--json", dest="jsonFile", required=True)
    parser.add_argument("-d", "--dir", dest="directory", required=True)
    return parser.parse_args()


def load_config(json_path):
    with open(json_path) as f:
        return json.load(f)


def extract_metadata(config):
    from core.extractors import RBNFExtractor, VirtExtractor, UMLExtractor
    syntax_type = config["syntax"]["type"]

    if syntax_type == "rbnf":
        with open(config["syntax"]["info"]["rbnfFile"]) as f:
            return RBNFExtractor(f.read()).extract()
    elif syntax_type == "virt":
        with open(config["syntax"]["info"]["virtFile"]) as f:
            return VirtExtractor(f.read()).extract()
    elif syntax_type == "uml":
        with open(config["syntax"]["info"]["umlFile"]) as f:
            return UMLExtractor(f.read()).extract()
    else:
        raise ValueError(f"Unsupported syntax type: {syntax_type}")


def generate_dsl_info(metadata, output_dir):
    from core.dsl_generator import DSLInfoGenerator
    generator = DSLInfoGenerator(metadata)
    generator.generate(pathlib.Path(output_dir) / "dsl_info.py")


def import_dsl_info(output_dir):
    spec = importlib.util.spec_from_file_location(
        "dsl_info",
        str(pathlib.Path(output_dir) / "dsl_info.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def process_pipeline(config, dsl_info, output_dir):
    # Инициализация компонентов с использованием dsl_info
    from implementations.dsl_scanner import DSLScanner
    from implementations.dsl_afterscanner import DSLAfterscanner

    scanner = DSLScanner(dsl_info)
    afterscanner = DSLAfterscanner(dsl_info)

    # Обработка кода
    with open(config["code"]["path"]) as f:
        tokens = scanner.tokenize(f.read())
        processed_tokens = afterscanner.process(tokens)

    # Построение AST
    from syntax import BuildAst
    ast = BuildAst(
        syntax_info=config["syntax"],
        axiom=dsl_info.axiom,
        tokens=processed_tokens
    )

    # Генерация диаграмм
    from core.dot_generator import DotGenerator
    DotGenerator(ast).generate(pathlib.Path(output_dir) / "diagrams")


if __name__ == "__main__":
    main()
