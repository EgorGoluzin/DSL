from DSLTools.models import GrammarObject

# Block with lexis
grammar_terminals = {terminals}

grammar_nonterminals = ['Alternative',.
	'Element',.
	'Group',.
	'Iteration',.
	'Optional',.
	'Rule',.
	'RuleElement',.
	'Sequence']

grammar_keywords = [('::=', Terminal.ebnf_symbol),
	(':', Terminal.ebnf_symbol),
	(';', Terminal.ebnf_symbol),
	('#', Terminal.ebnf_symbol),
	('(', Terminal.ebnf_symbol),
	(')', Terminal.ebnf_symbol),
	('[', Terminal.ebnf_symbol),
	(']', Terminal.ebnf_symbol),
	('{', Terminal.ebnf_symbol),
	('}', Terminal.ebnf_symbol),
	('|', Terminal.ebnf_symbol),
	('.', Terminal.ebnf_symbol),
	('RULES', Terminal.name)]

grammar_axiom = 'Rule'

# Block syntax rules



grammar_syntax_rules = {syntax_rules}

# New formed grammatical object
GrammarObject(terminals=grammar_terminals,
              non_terminals=grammar_nonterminals,
              keys=grammar_keywords,
              axiom=grammar_axiom,
              rules=grammar_syntax_rules)
