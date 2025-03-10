import re
from enum import Enum
from pathlib import Path

from DSLTools import Rule, Terminal
from DSLTools.models import MetaObject, GrammarObject
from DSLTools.utils.file_ops import load_config
from sly import Lexer, Parser

PROJECT_ROOT = Path(__file__).parent.parent


class EBNFLexer(Lexer):
    tokens = {
        # Секции
        'SECTION_TERMINALS',
        'SECTION_KEYS',
        'SECTION_NONTERMINALS',
        'SECTION_AXIOM',
        'SECTION_RULES',

        # Символы EBNF
        'LBRACE', 'RBRACE',
        'LBRACK', 'RBRACK',
        'PIPE', 'HASH', 'SEMI',
        'COLONEQ', 'COLON',
        'STRING', 'REGEX', 'IDENT',
    }

    ignore = ' \t'
    # ignore_comment = r'\#.*'

    # Секции
    SECTION_TERMINALS = r'TERMINALS:?'
    SECTION_KEYS = r'KEYS:?'
    SECTION_NONTERMINALS = r'NONTERMINALS:?'
    SECTION_AXIOM = r'AXIOM:?'
    SECTION_RULES = r'RULES:?'

    # Символы
    COLONEQ = r'::='
    COLON = r':'
    LBRACE = r'\{'
    RBRACE = r'\}'
    LBRACK = r"\["
    RBRACK = r"\]"
    PIPE = r'\|'
    HASH = r'\#'
    SEMI = r';'

    # Идентификаторы и литералы
    IDENT = r'[a-zA-Z_][a-zA-Z0-9_]*'

    @_(r"'[^']*'", r'"[^"]*"')
    def STRING(self, t):
        t.value = t.value[1:-1]
        return t

    @_(r'/[^/]+/')
    def REGEX(self, t):
        t.value = t.value[1:-1]
        return t

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')


class EBNFParser(Parser):
    tokens = EBNFLexer.tokens
    start = 'grammar'

    def __init__(self):
        self.grammar = GrammarObject()
        self.current_section = None
        self.messages = []  # Буфер для сообщений

    def add_message(self, level: str, message: str, lineno: int = None):
        """Добавляет сообщение в буфер."""
        self.messages.append({
            'level': level,
            'message': message,
            'lineno': lineno
        })

    def print_messages(self):
        """Выводит все сообщения."""
        for msg in self.messages:
            level = msg['level'].upper()
            lineno = f" (line {msg['lineno']})" if msg['lineno'] else ""
            print(f"[{level}]{lineno}: {msg['message']}")

    def parse(self, tokens):
        for token in tokens:
            print(f"Token: {token.type}, Value: {token.value}")
        super().parse(tokens)

    # Grammar structure
    @_('sections')
    def grammar(self, p):
        return self.grammar

    @_('sections section')
    def sections(self, p):
        pass

    @_('section')
    def sections(self, p):
        # self.current_section =
        pass

    # Sections handling
    @_('SECTION_TERMINALS COLON terminals',
       'SECTION_TERMINALS terminals')
    def section(self, p):
        print("Зашли в секцию терминалов")
        pass

    @_('SECTION_KEYS COLON keys',
       'SECTION_KEYS keys')
    def section(self, p):
        pass

    @_('SECTION_NONTERMINALS COLON nonterminals',
       'SECTION_NONTERMINALS nonterminals')
    def section(self, p):
        pass

    @_('SECTION_AXIOM COLON axiom',
       'SECTION_AXIOM axiom')
    def section(self, p):
        pass

    @_('SECTION_RULES COLON rules',
       'SECTION_RULES rules')
    def section(self, p):
        pass

    # Terminals
    @_('terminals terminal SEMI')
    def terminals(self, p):
        print('terminals terminal SEMI')
        pass

    @_('terminal SEMI')
    def terminals(self, p):
        print('terminal SEMI')
        pass

    @_('IDENT COLONEQ REGEX')
    def terminal(self, p):
        if p.IDENT in self.grammar.terminals:
            self.add_message('error', f"Terminal '{p.IDENT}' already defined", p.lineno)
        self.add_message('info', f"Added terminal: {p.IDENT}", p.lineno)
        self.grammar.terminals[p.IDENT] = Terminal(name=p.IDENT, pattern=p.REGEX)

    # Keys
    @_('keys key SEMI')
    def keys(self, p):
        pass

    @_('key SEMI')
    def keys(self, p):
        pass

    @_('STRING')
    def key(self, p):
        key = p.STRING
        for terminal in self.grammar.terminals.values():
            res = re.match(terminal.pattern, key)
            if res is not None:
                self.grammar.keys.append((terminal.name, key))
                self.add_message('info', f"Added key: {key} as {terminal.name}", p.lineno)
                break
        else:
            self.add_message('warning', f"No matching terminal for key: {key}", p.lineno)

    # Non-terminals
    @_('nonterminals nonterminal SEMI')
    def nonterminals(self, p):
        pass

    @_('nonterminal SEMI')
    def nonterminals(self, p):
        pass

    @_('IDENT')
    def nonterminal(self, p):
        if p.IDENT in self.grammar.non_terminals:
            self.add_message('warning', f"Non-terminal '{p.IDENT}' already defined", p.lineno)
        self.add_message('info', f"Added non-terminal: {p.IDENT}", p.lineno)
        self.grammar.non_terminals.append(p.IDENT)

    # Axiom
    @_('IDENT')
    def axiom(self, p):
        if p.IDENT not in self.grammar.non_terminals:
            self.add_message('error', f"Undefined non-terminal '{p.IDENT}' for axiom", p.lineno)
        self.add_message('info', f"Set axiom: {p.IDENT}", p.lineno)
        self.grammar.axiom = p.IDENT

    # Rules
    @_('rules rule SEMI')
    def rules(self, p):
        print("rules rule SEMI")
        pass

    @_('rule SEMI')
    def rules(self, p):
        print("rule SEMI")
        pass

    @_('IDENT COLONEQ alternatives')
    def rule(self, p):
        if p.IDENT not in self.grammar.non_terminals:
            self.add_message('error', f"Undefined non-terminal '{p.IDENT}' in rule", p.lineno)
        self.add_message('info', f"Added rule for: {p.IDENT}", p.lineno)
        try:
            self.grammar.rules[p.IDENT] = []
            for alt in p.alternatives:
                self.grammar.rules[p.IDENT].append(
                    Rule(lhs=p.IDENT, elements=alt))
                # self.print_messages()
        except KeyError:
            self.print_messages()
            raise "Bannn "

    @_('alternatives PIPE sequence')
    def alternatives(self, p):
        self.add_message('info', f"Check alternatives: {p.alternatives} {p.sequence}", p.lineno)
        return p.alternatives + [p.sequence]

    @_('sequence')
    def alternatives(self, p):
        self.add_message('info', f"Check seq: {p.sequence}", p.lineno)
        return [p.sequence]

    @_('elements')
    def sequence(self, p):
        return p.elements

    # Elements
    @_('elements element')
    def elements(self, p):
        return p.elements + [p.element]

    @_('element')
    def elements(self, p):
        self.add_message('info', f"Check els: {p.element}", p.lineno)
        return [p.element]

    @_('group', 'optional', 'IDENT', 'STRING')
    def element(self, p):
        self.add_message('info', f"Check el: {p[0]}", p.lineno)
        return p[0]

    @_('LBRACE element HASH STRING RBRACE')
    def group_with_separator(self, p):
        print("With Sep")
        return {
            'type': 'group',
            'elements': p.elements,
            'separator': p.STRING
        }

    @_('LBRACE elements RBRACE')
    def group(self, p):
        print(f"Group without separator: {p.elements}")
        return {'type': 'group', 'elements': p.elements, 'separator': None}

    @_('LBRACK elements RBRACK')
    def optional(self, p):
        return {'type': 'optional', 'elements': p.elements}

    def error(self, token):
        if token:
            msg = f"Syntax error at token '{token.value}'"
            self.add_message('error', msg, token.lineno)

        else:
            self.add_message('error', "Syntax error at EOF")
        self.print_messages()
        raise SyntaxError("Parsing failed")


json_path = r"C:\Users\Hp\PycharmProjects\DSL\DSLTools\examples\PSECO\pseco_mo.json"
config = load_config(json_path)
mo = MetaObject(config)
syntax_dir = mo.syntax["info"]["syntax_dir"]
syntax_path = rf"{PROJECT_ROOT}\{syntax_dir}\{mo.syntax['info']['filenames'][1]}"

with open(syntax_path, "r") as r:
    content = r.read()

lexer = EBNFLexer()
tokenso = lexer.tokenize(content)

for token_ in tokenso:
    print(f"Line {token_.lineno}: {token_.type} -> {token_.value}")
# parser = EBNFParser()
# result = parser.parse(tokenso)
# parser.print_messages()
# print(result)
# for token_ in :
#     print(f"Line {token_.lineno}: {token_.type} -> {token_.value}")
