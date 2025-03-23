import pathlib
import unittest
import re

from DSLTools.models.ast import ASTNode, NodeType
from dsl_info import Nonterminal, Terminal
from DSLTools.core.retranslator import ReToExpression
from DSLTools.utils.file_ops import validate_paths
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.resolve()
path_sample = validate_paths(PROJECT_ROOT, pathlib.Path("examples/rbnf/example.txt"), is_dir=False)


class TestRetranslator(unittest.TestCase):
    def setUp(self):
        self.ast = ASTNode(
            type=NodeType.NONTERMINAL,
            subtype=Nonterminal.EXPRESSIONS,
            children=[
                ASTNode(
                    type=NodeType.NONTERMINAL,
                    subtype=Nonterminal.EXPRESSION,
                    children=[
                        ASTNode(NodeType.TERMINAL, Terminal.number, value='4'),
                        ASTNode(NodeType.KEY, value='*'),
                        ASTNode(NodeType.TERMINAL, Terminal.number, value='4'),
                        ASTNode(NodeType.KEY, value='*'),
                        ASTNode(NodeType.TERMINAL, Terminal.number, value='4'),
                        ASTNode(NodeType.KEY, value='*'),
                        ASTNode(NodeType.TERMINAL, Terminal.number, value='4'),
                    ]
                ),
                ASTNode(NodeType.KEY, value=','),
                ASTNode(
                    type=NodeType.NONTERMINAL,
                    subtype=Nonterminal.EXPRESSION,
                    children=[
                        ASTNode(
                            type=NodeType.NONTERMINAL,
                            subtype=Nonterminal.TERM,
                            children=[ASTNode(NodeType.TERMINAL, Terminal.number, value='4')]
                        ),
                        ASTNode(NodeType.KEY, value='+'),
                        ASTNode(
                            type=NodeType.NONTERMINAL,
                            subtype=Nonterminal.TERM,
                            children=[ASTNode(NodeType.TERMINAL, Terminal.number, value='4')]
                        ),
                        ASTNode(NodeType.KEY, value='+'),
                        ASTNode(
                            type=NodeType.NONTERMINAL,
                            subtype=Nonterminal.TERM,
                            children=[ASTNode(NodeType.TERMINAL, Terminal.number, value='4')]
                        ),
                        ASTNode(NodeType.KEY, value='+'),
                        ASTNode(
                            type=NodeType.NONTERMINAL,
                            subtype=Nonterminal.TERM,
                            children=[ASTNode(NodeType.TERMINAL, Terminal.number, value='4')]
                        ),
                        ASTNode(NodeType.KEY, value='+'),
                        ASTNode(
                            type=NodeType.NONTERMINAL,
                            subtype=Nonterminal.TERM,
                            children=[ASTNode(NodeType.TERMINAL, Terminal.number, value='4')]
                        ),
                    ]
                ),
                ASTNode(NodeType.KEY, value=','),
                ASTNode(
                    type=NodeType.NONTERMINAL, subtype=Nonterminal.EXPRESSION,
                    children=[
                        ASTNode(
                            type=NodeType.NONTERMINAL, subtype=Nonterminal.TERM,
                            children=[
                                ASTNode(type=NodeType.TERMINAL, subtype=Terminal.number, value='4'),
                                ASTNode(NodeType.KEY, value='*'),
                                ASTNode(type=NodeType.TERMINAL, subtype=Terminal.number, value='4'),
                            ]),
                        ASTNode(type=NodeType.KEY, value='+'),
                        ASTNode(
                            type=NodeType.NONTERMINAL, subtype=Nonterminal.TERM,
                            children=[
                                ASTNode(type=NodeType.TERMINAL, subtype=Terminal.number, value='4')
                            ]
                        )
                    ]
                )
            ],
        )
    def test_for_expression(self):
        with open(path_sample, "r") as f:
            value = f.read()
        value = re.sub(r'[\n\s\t]+', '', value)
        ret = ReToExpression()
        expression = ret.translate(head=self.ast)
        self.assertEqual(expression, value)


if __name__ == "__main__":
    unittest.main()
