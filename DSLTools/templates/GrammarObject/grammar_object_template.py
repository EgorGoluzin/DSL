from DSLTools.models import GrammarObject

# Block with lexis
grammar_terminals = {{terminals}}

grammar_nonterminals = [{nonterminals}]

grammar_keywords = [{keywords}]

grammar_axiom = {axiom}

# Block syntax rules

{grammar_syntax}

grammar_syntax_rules = [{syntax_rules}]

# New formed grammatical object
GrammarObject(terminals=grammar_terminals,
              non_terminals=grammar_nonterminals,
              keys=grammar_keywords,
              axiom=grammar_axiom,
              syntax_info=grammar_syntax_rules)
