import pathlib
import unittest
import re

from DSLTools.models import Token
from DSLTools.models.ast import ASTNode, NodeType
from dsl_info import Nonterminal, Terminal
from DSLTools.core.retranslator import ReToExpression
from DSLTools.utils.file_ops import validate_paths

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.resolve()
path_sample = validate_paths(PROJECT_ROOT, pathlib.Path("examples/rbnf/example.txt"), is_dir=False)


class TestRetranslator(unittest.TestCase):
    def setUp(self):
        self.ast = ASTNode(
            type=ASTNode.Type.NONTERMINAL,
            subtype="EXPRESSIONS",
            children=[
                ASTNode(
                    type=ASTNode.Type.NONTERMINAL,
                    subtype="EXPRESSION",
                    children=[
                        ASTNode(type=ASTNode.Type.TOKEN,
                                subtype="number",
                                children=[],
                                nonterminalType='',
                                commands=[],
                                token=Token(
                                    terminalType='number',
                                    str_value=None,
                                    token_type=Token.Type.TERMINAL,
                                    value="2"),
                                value='2',
                                attribute=2),
                        ASTNode(type=ASTNode.Type.TOKEN,
                                subtype="*",
                                children=[],
                                nonterminalType='',
                                commands=[],
                                token=Token(
                                    terminalType=None,
                                    str_value="*",
                                    token_type=Token.Type.KEY,
                                    value="*"),
                                value='*',
                                attribute="*"),
                        ASTNode(type=ASTNode.Type.TOKEN,
                                subtype="number",
                                children=[],
                                nonterminalType='',
                                commands=[],
                                token=Token(
                                    terminalType='number',
                                    str_value=None,
                                    token_type=Token.Type.TERMINAL,
                                    value="5"),
                                value='5',
                                attribute=5)
                        ,
                        ASTNode(type=ASTNode.Type.TOKEN,
                                subtype="*",
                                children=[],
                                nonterminalType='',
                                commands=[],
                                token=Token(
                                    terminalType=None,
                                    str_value="*",
                                    token_type=Token.Type.KEY,
                                    value="*"),
                                value='*',
                                attribute="*"),

                        ASTNode(type=ASTNode.Type.TOKEN,
                                subtype="number",
                                children=[],
                                nonterminalType='',
                                commands=[],
                                token=Token(
                                    terminalType='number',
                                    str_value=None,
                                    token_type=Token.Type.TERMINAL,
                                    value="5"),
                                value='5',
                                attribute=5),

                        ASTNode(type=ASTNode.Type.TOKEN,
                                subtype="+",
                                children=[],
                                nonterminalType='',
                                commands=[],
                                token=Token(
                                    terminalType=None,
                                    str_value="+",
                                    token_type=Token.Type.KEY,
                                    value="+"),
                                value='+',
                                attribute="+"),

                        ASTNode(type=ASTNode.Type.TOKEN,
                                subtype="number",
                                children=[],
                                nonterminalType='',
                                commands=[],
                                token=Token(
                                    terminalType='number',
                                    str_value=None,
                                    token_type=Token.Type.TERMINAL,
                                    value="5"),
                                value='5',
                                attribute=5),
                    ]
                ),

            ],
        )

    def test_for_expression(self):
        value = "2*5*5+5"
        value = re.sub(r'[\n\s\t]+', '', value)
        ret = ReToExpression()
        expression = ret.translate(head=self.ast)
        self.assertEqual(expression, value)


if __name__ == "__main__":
    unittest.main()
