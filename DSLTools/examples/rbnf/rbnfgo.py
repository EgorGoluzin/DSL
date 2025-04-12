import os
import pathlib

from DSLTools.core.astgenerator import DefaultAstBuilder
from DSLTools.core.grammar_parsers import RBNFParser
from DSLTools.core.scanning import DefaultScanner
from DSLTools.core.tools import render_tree, get_parser
from DSLTools.core.wirth_diagram_generation import generate_dot
from DSLTools.models.tokens import Tokens
from DSLTools.utils.file_ops import load_config
from DSLTools.utils.wirth_render import render_dot_to_png
from DSLTools.models import GetSyntaxDesription, GrammarObject, Terminal, MetaObject
from settings import settings


names = ["Alternative", "Element", "Group", "Iteration", "Optional", "Rule", "RuleElement", "Sequence"]
directory_to_save_base = fr"{settings.PROJECT_ROOT}\examples"
directory_to_save = fr"{directory_to_save_base}\rbnf"
# print(GetSyntaxDesription(fr"{directory_to_save}\wirth", None))
# в эту структуру используя матрицу инцидентности и
# Узлы заранее определенные. Пока вполне достаточно использовать GetSyntaxDescription.

OurRules = GetSyntaxDesription(fr"{directory_to_save}\wirth", None)
# for lhs in OurRules:
#     print(f"{lhs=}", f"rhs = {OurRules[lhs]}")

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
    syntax_info=OurRules)

# grammar_names = ["PSECO", "ISDSL", "GRAPHS", "PUML", "CHAO"]
grammar_names = ["PSECO"]
rule_scanner = DefaultScanner(go)
builder = DefaultAstBuilder(debug=False)
for grammar in grammar_names:

    path_to_save_grammar = fr"{directory_to_save}\{grammar}"
    os.makedirs(path_to_save_grammar, exist_ok=True)

    json_path = fr"{directory_to_save_base}\{grammar}\metainfo.json"
    config = load_config(json_path)
    mo_cur = MetaObject(config)
    parser = RBNFParser()
    go_cur: GrammarObject = parser.parse(mo_cur)

    for rule_name, rule_in_cur_grammar in parser.store_for_rules:
        print(rule_in_cur_grammar)
        rule_dir = fr"{path_to_save_grammar}\ast_{rule_name}"

        os.makedirs(rule_dir, exist_ok=True)
        res = rule_scanner.tokenize(rule_in_cur_grammar)

        # with open(fr'{rule_dir}\tokens_{rule_name}.yaml', 'w') as file:
        #     file.write(Tokens(res).to_yaml())

        ast = builder.build(go, res)

        # with open(fr"{rule_dir}\ast_{rule_name}.yaml", 'w') as file:
        #     file.write(ast.to_yaml())

        # render_tree(f"ast_{rule_name}", ast, pathlib.Path(rule_dir))
