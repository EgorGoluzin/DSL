from DSLTools.models import GrammarObject, Terminal, Rule
from DSLTools.models.legacy_for_wirth import NodeTypeLegacy, NodeLegacy

# Block with lexis
grammar_terminals = {
    Terminal(name="key_name", pattern=r"\'[^\']*\'"),
    Terminal(name="name", pattern=r"[A-Za-z_][A-Za-z0-9_]*"),
    Terminal(name="ebnf_symbol", pattern=r"[::=#;(){}\[\]|.]"),
    Terminal(name="whitespace", pattern=r"\s+"),
}

grammar_nonterminals = [
    "Alternative",
    "Element",
    "Group",
    "Iteration",
    "Optional",
    "Rule",
    "RuleElement",
    "Sequence",
]

grammar_keywords = [
    ("::=", "ebnf_symbol"),
    (":", "ebnf_symbol"),
    (";", "ebnf_symbol"),
    ("#", "ebnf_symbol"),
    ("(", "ebnf_symbol"),
    (")", "ebnf_symbol"),
    ("[", "ebnf_symbol"),
    ("]", "ebnf_symbol"),
    ("{", "ebnf_symbol"),
    ("}", "ebnf_symbol"),
    ("|", "ebnf_symbol"),
    (".", "ebnf_symbol"),
    ("RULES", "name"),
]

grammar_axiom = "Rule"

# Block syntax rules


grammar_syntax_rules = {
    "Alternative": Rule(
        definition=[
            NodeLegacy(
                type="nonterminal",
                str_="Sequence",
                nonterminal="None",
                terminal="None",
                nextNodes=[],
            ),
            NodeLegacy(
                type="key", str_="|", nonterminal="None", terminal="None", nextNodes=[]
            ),
        ],
        node_matrix=[[0, 1, 0, 0], [0, 0, 1, 1], [0, 1, 0, 0], [0, 0, 0, 0]],
    ),
    "Sequence": Rule(
        definition=[
            NodeLegacy(
                type="nonterminal",
                str_="RuleElement",
                nonterminal="None",
                terminal="None",
                nextNodes=[],
            )
        ],
        node_matrix=[[0, 1, 0], [0, 1, 1], [0, 0, 0]],
    ),
    "RuleElement": Rule(
        definition=[
            NodeLegacy(
                type="nonterminal",
                str_="Element",
                nonterminal="None",
                terminal="None",
                nextNodes=[],
            ),
            NodeLegacy(
                type="nonterminal",
                str_="Group",
                nonterminal="None",
                terminal="None",
                nextNodes=[],
            ),
            NodeLegacy(
                type="nonterminal",
                str_="Optional",
                nonterminal="None",
                terminal="None",
                nextNodes=[],
            ),
            NodeLegacy(
                type="nonterminal",
                str_="Iteration",
                nonterminal="None",
                terminal="None",
                nextNodes=[],
            ),
        ],
        node_matrix=[
            [0, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0],
        ],
    ),
}

# New formed grammatical object
stored_go = GrammarObject(
    terminals=grammar_terminals,
    non_terminals=grammar_nonterminals,
    keys=grammar_keywords,
    axiom=grammar_axiom,
    rules=grammar_syntax_rules,
)

wirth_dest = r"C:\WORK\DSL\DSLTools\core\wirth_dest"

stored_go.rules_to_dot_files(wirth_dest)

stored_go.upload(wirth_dest)
