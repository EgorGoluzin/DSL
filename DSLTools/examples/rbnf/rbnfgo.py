from DSLTools.core.astgenerator import DefaultAstBuilder
from DSLTools.core.scanning import DefaultScanner
from DSLTools.core.wirth_diagram_generation import generate_dot
from DSLTools.models.tokens import Tokens
from DSLTools.utils.wirth_render import render_dot_to_png
from DSLTools.models import GetSyntaxDesription, GrammarObject, Terminal

names = ["Alternative", "Element", "Group", "Iteration", "Optional", "Rule", "RuleElement", "Sequence"]
directory_to_save = r"C:\Users\Hp\PycharmProjects\DSL\DSLTools\examples\rbnf"
# print(GetSyntaxDesription(fr"{directory_to_save}\wirth", None))
"""
syntaxInfo = {'Sequence': NodeLegacy(type= 'start', 
                                    str_= 'Sequence', 
                                    nonterminal='None', 
                                    terminal='None', 
                                    nextNodes=[
                                    (NodeLegacy(
                                        type= 'nonterminal', 
                                        str_= 'RuleElement', 
                                        nonterminal= '
                                        RuleElement', 
                                        terminal= 'None', 
                                        nextNodes= [
                                        (NodeLegacy(
                                            type= 'nonterminal', 
                                            str_= 'RuleElement', 
                                            nonterminal= 'RuleElement', 
                                            terminal= 'None', 
                                            nextNodes= [(...)
                                                (NodeLegacy(type= 'end', 
                                                str_= '', 
                                                nonterminal= 'None', 
                                                terminal= 'None', 
                                                nextNodes= []), '')]), '')
                                                (NodeLegacy(type= 'end', 
                                                str_= '', 
                                                nonterminal= 'None', 
                                                terminal= 'None', 
                                                nextNodes= []), 
                                                '')]), '')])
"""

# TODO: Если пытаться писать сериализацию в Py нужно написать перевод
# в эту структуру используя матрицу инцидентности и
# Узлы заранее определенные. Пока вполне достаточно использовать GetSyntaxDescription.

OurRules = GetSyntaxDesription(fr"{directory_to_save}\wirth", None)
# for lhs in OurRules:
#     print(f"{lhs=}", f"rhs = {OurRules[lhs]}")

go = GrammarObject(terminals={
    "key_name": Terminal(name="key_name", pattern=r'\'[A-Za-z_][A-Za-z0-9_]*\''),
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

scanner = DefaultScanner(go)

input_str = "Conditional      ::= 'IF' Expression 'THEN' Block [ { 'ELSEIF' Expression 'THEN' Block } ] [ 'ELSE' Block ] 'END_IF';"
file_name = "ast_conditional"
res = scanner.tokenize(input_str)
# res_tmp = []
# for it in res:
#     if it.terminalType != "regular_expression":
#         res_tmp.

for name in names:
    cur_path = fr"{directory_to_save}\wirth\{name}.gv"
    # render_dot_to_png(cur_path, fr"{directory_to_save}\wirthpng")
    with open(fr'{directory_to_save}\tokens.yaml', 'w') as file:
        file.write(Tokens(res).to_yaml())

    builder = DefaultAstBuilder()

    ast = builder.build(go, res)
    with open(fr"{directory_to_save}\{file_name}.yaml", 'w') as file:
        file.write(ast.to_yaml())

