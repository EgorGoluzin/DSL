from DSLTools.core.wirth_diagram_generation import generate_dot
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

#TODO: Если пытаться писать сериализацию в Py нужно написать перевод
# в эту структуру используя матрицу инцидентности и
# Узлы заранее определенные. Пока вполне достаточно использовать GetSyntaxDescription.

OurRules = GetSyntaxDesription(fr"{directory_to_save}\wirth", None)
# for lhs in OurRules:
#     print(f"{lhs=}", f"rhs = {OurRules[lhs]}")

GrammarObject(terminals={"name": Terminal(name="name", pattern='[A-Za-z_][A-Za-z0-9_]*'),
                         "key_name": Terminal(name="key_name", pattern='\'[^\']*\''),
                         "regular_expression": Terminal(name="regular_expression", pattern="[^\\']*(\\.[^\\']*)*"),
                         "ebnf_symbol": Terminal(name="ebnf_symbol", pattern="[::=#;(){}\[\]|.]"),
                         "whitespace": Terminal(name="whitespace", pattern="\s+")},
              non_terminals=["Alternative", "Element", "Group",
                             "Iteration", "Optional",
                             "Rule", "RuleElement",
                             "Sequence", "RuleBlock"],
              keys=[("ebnf_symbol", ':'),
                    ("ebnf_symbol", ';'),
                    ("ebnf_symbol", '::='),
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
              axiom="RuleBlock",
              syntax_info=OurRules)


for name in names:
    cur_path = fr"{directory_to_save}\wirth\{name}.gv"
    render_dot_to_png(cur_path, fr"{directory_to_save}\wirthpng")