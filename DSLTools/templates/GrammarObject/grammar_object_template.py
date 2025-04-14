from DSLTools.models import GrammarObject, Terminal, Rule
from DSLTools.models.legacy_for_wirth import NodeTypeLegacy, NodeLegacy

# Block with lexis
grammar_terminals = {{ {terminals} }}

grammar_nonterminals = [{nonterminals}]

grammar_keywords = [{keywords}]

grammar_axiom = {axiom}

# Block syntax rules


grammar_syntax_rules = {{ {syntax_rules} }}

# New formed grammatical object
stored_go = GrammarObject(terminals=grammar_terminals,
              non_terminals=grammar_nonterminals,
              keys=grammar_keywords,
              axiom=grammar_axiom,
              rules=grammar_syntax_rules)

wirth_dest = {wirth_dest}

stored_go.rules_to_dot_files(wirth_dest)

stored_go.upload(wirth_dest)
