from DSLTools.models import GrammarObject, Terminal, Rule
from DSLTools.models.legacy_for_wirth import NodeTypeLegacy, NodeLegacy
from pathlib import Path
import time

# Block with lexis
grammar_terminals = {
    "number": Terminal(name="number", pattern=r"[1-9]\d*"),
    "operation": Terminal(name="operation", pattern=r"[\+\*]"),
    "terminator": Terminal(name="terminator", pattern=r","),
}

grammar_nonterminals = ["EXPRESSIONS", "EXPRESSION", "TERM"]

grammar_keywords = [("operation", "+"), ("operation", "*"), ("terminator", ",")]

grammar_axiom = "EXPRESSIONS"

# Block syntax rules


grammar_syntax_rules = {
    "EXPRESSIONS": Rule(
        definition=[
            NodeLegacy(
                type="nonterminal",
                str_="EXPRESSION",
                nonterminal="None",
                terminal="None",
                nextNodes=[],
            ),
            NodeLegacy(
                type="key", str_=",", nonterminal="None", terminal="None", nextNodes=[]
            ),
        ],
        node_matrix=[[0, 1, 0, 0], [0, 0, 1, 1], [0, 1, 0, 0], [0, 0, 0, 0]],
    ),
    "EXPRESSION": Rule(
        definition=[
            NodeLegacy(
                type="nonterminal",
                str_="TERM",
                nonterminal="None",
                terminal="None",
                nextNodes=[],
            ),
            NodeLegacy(
                type="key", str_="+", nonterminal="None", terminal="None", nextNodes=[]
            ),
        ],
        node_matrix=[[0, 1, 0, 0], [0, 0, 1, 1], [0, 1, 0, 0], [0, 0, 0, 0]],
    ),
    "TERM": Rule(
        definition=[
            NodeLegacy(
                type="terminal",
                str_="number",
                nonterminal="None",
                terminal="None",
                nextNodes=[],
            ),
            NodeLegacy(
                type="key", str_="*", nonterminal="None", terminal="None", nextNodes=[]
            ),
        ],
        node_matrix=[[0, 1, 0, 0], [0, 0, 1, 1], [0, 1, 0, 0], [0, 0, 0, 0]],
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

wirth_dest = Path(r"C:\WORK\DSL\DSLTools\core\wirth_dest") / str(time.time_ns())

stored_go.rules_to_dot_files(wirth_dest)

stored_go.upload(wirth_dest)
