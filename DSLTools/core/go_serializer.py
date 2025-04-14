from pathlib import Path
from DSLTools.models import GrammarObject

DSLINFOTEMPLATENAME = Path(__file__).parent.parent.resolve() / Path(r"templates\GrammarObject\grammar_object_template.py")

class GrammarObjectSerializer:
    def serialize(self, go: GrammarObject, dest: Path):
        filename = Path("grammar_object.py")
        with open(DSLINFOTEMPLATENAME, 'r') as templateFile:
            templateText = templateFile.read()

        with open(dest / filename, 'w') as file:
            file.write(templateText.format(
                terminals=go.serialized_terminals(),
                nonterminals=go.serialized_nonterminals(),
                keywords=go.serialized_keys(),
                axiom=go.serialized_axiom(),
                grammar_syntax=''
            ))
