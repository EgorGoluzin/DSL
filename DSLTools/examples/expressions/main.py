import re
import sys
import pathlib
import time

from DSLTools.core.tools import get_parser
from DSLTools.core.wirth_diagram_generation import generate_dot
from DSLTools.models import (MetaObject, TypeParse, IGrammarParser, GrammarObject)
from DSLTools.utils.file_ops import validate_paths, load_config, generate_file
from DSLTools.core.scanning import DefaultScanner
from DSLTools.core.rule_wirth_converter import convert_rules_to_diagrams
from DSLTools.core.astgenerator import GeneralizedParser, DefaultAstBuilder
from DSLTools.utils.wirth_render import render_dot_to_png
from DSLTools.core.astgenerator import DefaultAstBuilder
from DSLTools.models.ast import ASTNode, EvalContext, EvalRegistry
from DSLTools.models.tokens import Tokens
from settings import settings
from DSLTools.core.retranslator import ReToExpression
from DSLTools.implementations.token_post_processor import ExprEvalMatch, ExprEvalAttrs
from DSLTools.core.tokenpostprocessing import TokenPostProcessingManager

PROJECT_ROOT = settings.PROJECT_ROOT

class ExpressionsEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        context.warnings.append('Calculating Expressions')
        return ('[' +
                ', '.join(
                    str(children[i].evaluated(context))
                    for i in range(0, len(children), 2)
                )
                + ']'
                )

class ExpressionEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        _sum = 0
        for i in range(0, len(children), 2):
            _sum += children[i].evaluated(context)
        return _sum

class TermEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        cum = 1
        for i in range(0, len(children), 2):
            cum *= children[i].evaluated(context)
        return cum

class NumberEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        return int(value)

class KeyEval(ASTNode.IAttrEval):
    def __call__(self, value: str, children: list[ASTNode], context):
        return value

class ProgramEval(ASTNode.IAttrEval):
    def __init__(self, name: str):
        self.name = name

    def __call__(self, value, children, context):
        print(f'ProgramEval name: {self.name = }')
        return self.name

expressions_eval = ExpressionsEval()
expression_eval = ExpressionEval()
term_eval = TermEval()
number_eval = NumberEval()
key_eval = KeyEval()

evaluators = {
    (ASTNode.Type.TOKEN, 'number'): number_eval,
    (ASTNode.Type.TOKEN, '+'): key_eval,
    (ASTNode.Type.TOKEN, '*'): key_eval,
    (ASTNode.Type.TOKEN, ','): key_eval,
    (ASTNode.Type.NONTERMINAL, 'TERM'): term_eval,
    (ASTNode.Type.NONTERMINAL, 'EXPRESSION'): expression_eval,
    (ASTNode.Type.NONTERMINAL, 'EXPRESSIONS'): expressions_eval,
}

EvalRegistry.register(ASTNode.Type.TOKEN, 'number', number_eval)
EvalRegistry.register(ASTNode.Type.TOKEN, '+', key_eval)
EvalRegistry.register(ASTNode.Type.TOKEN, '*', key_eval)
EvalRegistry.register(ASTNode.Type.TOKEN, ',', key_eval)
EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'TERM', term_eval)
EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'EXPRESSION', expression_eval)
EvalRegistry.register(ASTNode.Type.NONTERMINAL, 'EXPRESSIONS', expressions_eval)

def main():
    json_path = fr"{PROJECT_ROOT}\DSLTools\examples\expressions\metainfo.json"
    directory_to_save = fr"{PROJECT_ROOT}\DSLTools\examples\expressions"
    sample_file_path = fr"{PROJECT_ROOT}\DSLTools\examples\expressions\test.smpl"
    output_dir = pathlib.Path(sample_file_path).parent / "asts"
    output_dir.mkdir(parents=True, exist_ok=True)


    unhappy_files = []
    config = load_config(json_path)
    mo = MetaObject(config)
    parser = get_parser(mo)
    go = parser.parse(mo)
    go.upload(pathlib.Path(fr"{directory_to_save}\wirth"))
    print(go)

    scanner = DefaultScanner(go)
    with open(sample_file_path) as f:
        input_str = f.read()

    res = scanner.tokenize(input_str)
    with open('tokens.yaml', 'w') as file:
        file.write(Tokens(res).to_yaml())

    print("\n".join([item.__repr__() for item in res]))
    builder = DefaultAstBuilder(debug=True)
    try:
        ast = builder.build(go, res).attach_evaluators({
            (ASTNode.Type.NONTERMINAL, 'Program'): ProgramEval("test")
        })
        context = EvalContext()
        evaluated = ast.evaluated(context)
        print(f'Result: {evaluated}, {context}')
        output_file = output_dir / "expressions_ast.yaml"
        with open(output_file, 'w') as file:
            file.write(ast.to_yaml())
        print(f'Finished processing test.smpl. AST saved to {output_file}')
    except Exception as e:
        unhappy_files.append({
            'File': 'test.smpl',
            'Message': str(e)
        })

    for info in unhappy_files:
        print(f"File: {info['File']}")
        print(f"Message: {info['Message']}")
        print('-' * 20)

if __name__ == "__main__":
    main()