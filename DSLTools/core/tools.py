# Пока здесь будут располагаться функции, которые впоследствии перекочуют в основной функциональный объект
from pathlib import Path
import importlib.util
from DSLTools.models import IGrammarParser
from DSLTools.core.grammar_parsers import RBNFParser
from DSLTools.models import MetaObject, TypeParse, GrammarObject


# Вспомогательные функции
def get_parser(metadata: MetaObject) -> IGrammarParser:
    ## TODO: Заменить на мапу
    if metadata.type_to_parse == TypeParse.RBNF:
        return RBNFParser()


def generate_dsl_info(dest: Path, go: GrammarObject):
    from DSLTools.core.dsl_generator import DSLInfoGenerator
    generator = DSLInfoGenerator()
    generator.generate_dsl_info(go=go, dest=dest)


def import_dsl_info(output_dir):
    spec = importlib.util.spec_from_file_location(
        "dsl_info",
        str(Path(output_dir) / "dsl_info.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
