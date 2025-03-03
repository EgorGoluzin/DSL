from enum import Enum


class Terminal(Enum):
	name = 'name'
	number = 'number'
	symbol = 'symbol'
	text = 'text'
	whitespace = 'whitespace'

tokenRegularExpressions = [(Terminal.name, r'[A-Za-z_][A-Za-z0-9_]*'),
	(Terminal.number, r'[0-9]+'),
	(Terminal.symbol, r'[:=#;(){}\[\]|.,<>+]'),
	(Terminal.text, r'[^"]*'),
	(Terminal.whitespace, r'\s+')]


keys = [('IF', Terminal.name),
	('THEN', Terminal.name),
	('ELSE', Terminal.name),
	('ELSEIF', Terminal.name),
	('END_IF', Terminal.name),
	('FOR', Terminal.name),
	('DO', Terminal.name),
	('END_FOR', Terminal.name),
	('REPEAT', Terminal.name),
	('UNTIL', Terminal.name),
	('WHILE', Terminal.name),
	('END_WHILE', Terminal.name),
	('FUNC', Terminal.name),
	('END_FUNC', Terminal.name),
	('PROC', Terminal.name),
	('END_PROC', Terminal.name),
	('ITERATOR', Terminal.name),
	('END_ITERATOR', Terminal.name),
	('INPUT', Terminal.name),
	('OUTPUT', Terminal.name),
	('GOTO', Terminal.name),
	('ARRAY', Terminal.name),
	('STRUCT', Terminal.name),
	('SELECT', Terminal.name),
	('YIELD', Terminal.name),
	('RETURN', Terminal.name),
	('NEXT', Terminal.name),
	('FROM', Terminal.name),
	('TO', Terminal.name),
	('IN', Terminal.name),
	('{', Terminal.symbol),
	('}', Terminal.symbol),
	(':', Terminal.symbol),
	(';', Terminal.symbol),
	('>', Terminal.symbol),
	('+', Terminal.symbol)]


class Nonterminal(Enum):
	Program = 'Program'
	Statement = 'Statement'
	Block = 'Block'
	Expression = 'Expression'
	FunctionCall = 'FunctionCall'
	Arguments = 'Arguments'
	Parameters = 'Parameters'
	Range = 'Range'
	Set = 'Set'
	Variable = 'Variable'
	Identifier = 'Identifier'
	Number = 'Number'
	Text = 'Text'
	Assignment = 'Assignment'
	Conditional = 'Conditional'
	Loop = 'Loop'
	LC = 'LC'
	LA = 'LA'
	LB = 'LB'
	LS = 'LS'
	FunctionDecl = 'FunctionDecl'
	ProcDecl = 'ProcDecl'
	IteratorDecl = 'IteratorDecl'
	Input = 'Input'
	Output = 'Output'
	Comment = 'Comment'
	Goto = 'Goto'
	ArrayDecl = 'ArrayDecl'
	StructDecl = 'StructDecl'
	FieldDecl = 'FieldDecl'
	Select = 'Select'
	Yield = 'Yield'
	Return = 'Return'
	NextFor = 'NextFor'

axiom = Nonterminal.Program
