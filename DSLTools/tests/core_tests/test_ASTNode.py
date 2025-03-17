import pathlib
import unittest
import re

from DSLTools.models.ast import ASTNode, NodeType
from dsl_info import Nonterminal, Terminal
from DSLTools.core.retranslator import ReToExpression
from DSLTools.utils.file_ops import validate_paths
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.resolve()
path_sample = validate_paths(PROJECT_ROOT, pathlib.Path("examples/rbnf/example.txt"), is_dir=False)


class TestASTNode(unittest.TestCase):
    class TermEval:
        def __call__(self, *args, **kwds):
            value = args[0]
            children = 
    def setUp(self):
        self.term_eval = 
    def term():
        return ASTNode(
            'nonterminal', 'TERM',
            [
                
            ]
        )

    def test_for_expression(self):
        ast = ASTNode(...)
        print(ast.evaluate())


if __name__ == "__main__":
    unittest.main()
