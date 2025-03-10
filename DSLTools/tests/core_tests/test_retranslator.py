import unittest
from DSLTools.models.ast import ASTNode, NodeType
from dsl_info import Nonterminal, Terminal

class TestDefaultScanner(unittest.TestCase):
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



if __name__ == "__main__":
    unittest.main()
