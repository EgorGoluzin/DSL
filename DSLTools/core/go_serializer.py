from pathlib import Path
from DSLTools.models import GrammarObject, Terminal, Rule
from DSLTools.models.legacy_for_wirth import NodeTypeLegacy as NTL, NodeLegacy


DSLINFOTEMPLATENAME = Path(__file__).parent.parent.resolve() / Path(r"templates\GrammarObject\grammar_object_template.py")


class GrammarObjectSerializer:
    def serialize(self, go: GrammarObject, dest: Path, wirth_dest: Path):
        filename = Path("grammar_object_ser.py")
        with open(DSLINFOTEMPLATENAME, 'r') as templateFile:
            templateText = templateFile.read()
        print(f"Filename: {dest / filename}")
        with open(dest / filename, 'w') as file:
            file.write(templateText.format(
                terminals=go.serialized_terminals(),
                nonterminals=go.serialized_nonterminals(),
                keywords=go.serialized_keys(),
                axiom=go.serialized_axiom(),
                syntax_rules=go.serialized_rules(),
                wirth_dest=fr"r'{str(wirth_dest)}'",
            ))


if __name__ == '__main__':
    dest = Path(__file__).resolve().parent
    wirth_dest = dest / 'wirth_dest'
    go = GrammarObject(terminals={
        "number": Terminal(name="number", pattern=r'[1-9]\d*'),
        "operation": Terminal(name="operation", pattern=r'[\+\*]'),
        "terminator": Terminal(name="terminator", pattern=','),
        },
        non_terminals=["EXPRESSIONS", "EXPRESSION", "TERM"],
        keys=[("operation", '+'),
              ("operation", '*'),
              ("terminator", ','),],
        axiom="EXPRESSIONS",
        # Alternative       ::= { Sequence # '|' };
        # Sequence          ::= { RuleElement };
        # RuleElement       ::= Element | Group | Optional | Iteration;
        rules={
            # EXPRESSIONS ::= { EXPRESSION # , }
            'EXPRESSIONS': Rule(
                definition=[NodeLegacy(NTL.NONTERMINAL, 'EXPRESSION'),
                            NodeLegacy(NTL.KEY, ',')],
                node_matrix=[
                    [0, 1, 0, 0],
                    [0, 0, 1, 1],
                    [0, 1, 0, 0],
                    [0, 0, 0, 0],
                ]
            ),
            # EXPRESSION ::= { TERM # + }
            'EXPRESSION': Rule(
                definition=[NodeLegacy(NTL.NONTERMINAL, 'TERM'),
                            NodeLegacy(NTL.KEY, '+')],
                node_matrix=[
                    [0, 1, 0, 0],
                    [0, 0, 1, 1],
                    [0, 1, 0, 0],
                    [0, 0, 0, 0],
                ]
            ),
            # TERM ::= { number # * }
            'TERM': Rule(
                definition=[NodeLegacy(NTL.TERMINAL, 'number'),
                            NodeLegacy(NTL.KEY, '*'),],
                node_matrix=[
                    [0, 1, 0, 0],
                    [0, 0, 1, 1],
                    [0, 1, 0, 0],
                    [0, 0, 0, 0],
                ]
            ),
        })
    # print(f'Path: {__file__}')
    serializer = GrammarObjectSerializer()
    serializer.serialize(go, dest, wirth_dest)
