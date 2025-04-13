# Пока здесь будут располагаться функции, которые впоследствии перекочуют в основной функциональный объект
from pathlib import Path
import importlib.util

import graphviz

from DSLTools.models import IGrammarParser, ASTNode
from DSLTools.core.grammar_parsers import RBNFParser
from DSLTools.models import MetaObject, TypeParse, GrammarObject


# Вспомогательные функции
def get_parser(metadata: MetaObject) -> IGrammarParser:
    ## TODO: Заменить на мапу
    if metadata.type_to_parse == TypeParse.RBNF:
        return RBNFParser()


def generate_dsl_info(dest: Path, go: GrammarObject):
    from DSLTools.core.dsl_generator import DSLInfoGenerator
    generator = DSLInfoGenerator()
    generator.generate_dsl_info(go=go, dest=dest)


def import_dsl_info(output_dir):
    spec = importlib.util.spec_from_file_location(
        "dsl_info",
        str(Path(output_dir) / "dsl_info.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def render_tree(diagram_name: str, ast: ASTNode, path_to_save: Path):
    if path_to_save is None:
        return
    h = graphviz.Digraph(diagram_name, format='svg')
    i = 1
    nodes = [(ast, 0)]
    while len(nodes):
        node = nodes[0]
        if ASTNode.Type.NONTERMINAL == node[0].type:
            h.node(str(i),
                   f"NONTERMINAL\ntype: {node[0].nonterminalType}" + (f"\nattribute: {node[0].attribute}" if node[0].attribute else ""),
                   shape='box')
            if node[1] != 0:
                h.edge(str(node[1]), str(i))
            nodes += [(child, i) for child in node[0].children]
        else:

            if ASTNode.Type.TOKEN == node[0].type and node[0].subtype != node[0].value:
                h.node(str(i),
                       f"TERMINAL\ntype: {node[0].token.terminalType}\nstring: {node[0].value}" + (f"\nattribute: {node[0].attribute}" if node[0].attribute else ""),
                       shape='diamond')
            elif ASTNode.Type.TOKEN == node[0].type:
                h.node(str(i), f"KEY\nstring: {node[0].token.str}" + (f"\nattribute: {node[0].token.attribute}" if node[0].token.attribute else ""), shape='oval')
            h.edge(str(node[1]), str(i))
        nodes = nodes[1:]
        i += 1
    h.render(directory=path_to_save, view=True)