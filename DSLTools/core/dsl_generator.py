from pathlib import Path
from DSLTools.models import GrammarObject

DSLINFOTEMPLATENAME = Path(__file__).parent.parent.resolve() / Path(r"templates\sgi\dsl_info_template.py")

class DSLInfoGenerator:
    def generate_dsl_info(self, go: GrammarObject, dest: Path):
        # Генерация dsl_info.
        filename = Path("dsl_info.py")
        # Читаем файлик с шаблоном.
        with open(DSLINFOTEMPLATENAME, 'r') as templateFile:
            templateText = templateFile.read()

        with open(dest / filename, 'w') as file:
            file.write(templateText.format(
                terminals=go.get_terminals_for_template(),
                terminals_regex=go.get_regular_expression_for_template(),
                keys=go.get_keys_for_template(),
                nonterminals=go.get_non_terminals_for_template(),
                axiom=go.axiom))

        pass

    def generate_attribute_evaluator(self):
        # Генерация attribute_evaluator.py
        pass
