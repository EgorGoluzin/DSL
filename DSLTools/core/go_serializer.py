from pathlib import Path
from DSLTools.models import GrammarObject, Terminal, Rule
from DSLTools.models.legacy_for_wirth import NodeTypeLegacy as NTL, NodeLegacy


DSLINFOTEMPLATENAME = Path(__file__).parent.parent.resolve() / Path(r"templates\GrammarObject\grammar_object_template.py")


class GrammarObjectSerializer:
    def serialize(self, go: GrammarObject, dest: Path):
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
                syntax_rules=go.serialized_rules()
            ))


if __name__ == '__main__':
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
        # Alternative       ::= { Sequence # '|' };
        # Sequence          ::= { RuleElement };
        # RuleElement       ::= Element | Group | Optional | Iteration;
        rules={
            'Alternative': Rule(
                definition=[NodeLegacy(NTL.NONTERMINAL, 'Sequence'),
                            NodeLegacy(NTL.KEY, '|')],
                node_matrix=[
                    [0, 1, 0, 0],
                    [0, 0, 1, 1],
                    [0, 1, 0, 0],
                    [0, 0, 0, 0],
                ]
            ),
            'Sequence': Rule(
                definition=[NodeLegacy(NTL.NONTERMINAL, 'RuleElement')],
                node_matrix=[
                    [0, 1, 0],
                    [0, 1, 1],
                    [0, 0, 0],
                ]
            ),
            'RuleElement': Rule(
                definition=[NodeLegacy(NTL.NONTERMINAL, 'Element'),
                            NodeLegacy(NTL.NONTERMINAL, 'Group'),
                            NodeLegacy(NTL.NONTERMINAL, 'Optional'),
                            NodeLegacy(NTL.NONTERMINAL, 'Iteration')],
                node_matrix=[
                    [0, 1, 1, 1, 1, 0],
                    [0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 0],
                ]
            ),
        })
    # print(f'Path: {__file__}')
    serializer = GrammarObjectSerializer()
    dest = Path(__file__).resolve().parent
    serializer.serialize(go, dest)
