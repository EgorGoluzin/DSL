import pathlib
import unittest
from DSLTools.models.ast import ASTNode, NodeType
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.resolve()


class TestASTNode(unittest.TestCase):
    class TermEval:
        def __call__(self, value: str, children: list[ASTNode]):
            cum = 1
            for i in range(0, len(children), 2):
                cum *= children[i].evaluated()
            return cum

    class NumberEval:
        def __call__(self, value: str, children: list[ASTNode]):
            return int(value)

    class KeyEval:
        def __call__(self, value: str, children: list[ASTNode]):
            return value

    def setUp(self):
        self.term_eval = self.TermEval()
        self.number_eval = self.NumberEval()
        self.key_eval = self.KeyEval()

    def simple_term(self):
        return ASTNode(
            'nonterminal', 'TERM',
            [
                ASTNode(NodeType.TERMINAL, 'number', [], '4', evaluation=self.number_eval),
                ASTNode(NodeType.KEY, value='*', evaluation=self.key_eval),
                ASTNode(NodeType.TERMINAL, 'number', [], '4', evaluation=self.number_eval),
                ASTNode(NodeType.KEY, value='*', evaluation=self.key_eval),
                ASTNode(NodeType.TERMINAL, 'number', [], '4', evaluation=self.number_eval),
                ASTNode(NodeType.KEY, value='*', evaluation=self.key_eval),
                ASTNode(NodeType.TERMINAL, 'number', [], '4', evaluation=self.number_eval),
                ASTNode(NodeType.KEY, value='*', evaluation=self.key_eval),
                ASTNode(NodeType.TERMINAL, 'number', [], '4', evaluation=self.number_eval),
            ],
            evaluation=self.term_eval
        )

    def test_term_evaluation(self):
        ast = self.simple_term()
        self.assertEqual(1024, ast.evaluated())

    def test_term_to_json(self):
        ast = self.simple_term()
        ast.evaluated()
        # print(ast.to_json())
        expected = '''{
    type: 'nonterminal',
    subtype: 'TERM',
    value: '',
    attribute: '1024',
    children: [
        {
            type: 'terminal',
            subtype: 'number',
            value: '4',
            attribute: '4',
            children: []
        },
        {
            type: 'key',
            subtype: '',
            value: '*',
            attribute: '',
            children: []
        },
        {
            type: 'terminal',
            subtype: 'number',
            value: '4',
            attribute: '4',
            children: []
        },
        {
            type: 'key',
            subtype: '',
            value: '*',
            attribute: '',
            children: []
        },
        {
            type: 'terminal',
            subtype: 'number',
            value: '4',
            attribute: '4',
            children: []
        },
        {
            type: 'key',
            subtype: '',
            value: '*',
            attribute: '',
            children: []
        },
        {
            type: 'terminal',
            subtype: 'number',
            value: '4',
            attribute: '4',
            children: []
        },
        {
            type: 'key',
            subtype: '',
            value: '*',
            attribute: '',
            children: []
        },
        {
            type: 'terminal',
            subtype: 'number',
            value: '4',
            attribute: '4',
            children: []
        }
    ]
}
'''
        self.assertEqual(ast.to_json(), expected)


if __name__ == "__main__":
    unittest.main()
