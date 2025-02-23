from DSLTools.models.ast import TreeNode
class ASTProcessor:
    def __init__(self, ast_root: TreeNode):
        self.ast_root = ast_root
        self.terminals = []
        self.keys = []
        self.nonterminals = []
        self.axiom = None
        self.rules = []

    def extract_dsl_info(self):
        for child in self.ast_root.childs:
            if child.nonterminal_type == "TERMINALS_BLOCK":
                self.terminals = child.attribute
            elif child.nonterminal_type == "KEYS_BLOCK":
                self.keys = child.attribute
            # ... аналогично для других блоков

    def validate_grammar(self):
        # Валидация аксиомы и правил
        pass