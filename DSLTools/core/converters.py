from models.interface import IGrammarConverter, IVisualRepresentation
from models.parse import Rule, Iteration, GrammarObject
from pathlib import Path


class RBNFConverter(IGrammarConverter):
    @staticmethod
    def generate(rule: Rule) -> str:
        lines = []
        for alt in rule.alternatives:
            parts = []
            for elem in alt:
                if isinstance(elem, Iteration):
                    iter_part = f"{' '.join(map(str, elem.elements))}"
                    if elem.separator:
                        iter_part += f" # {elem.separator}"
                    iter_part += " }"
                    parts.append(iter_part)
                else:
                    parts.append(str(elem))
            lines.append(" ".join(parts))
        return f"{rule.name} ::= " + " |\n    ".join(lines) + " ."
    
    def convert(self, go: GrammarObject, dest: Path) -> None:
        return super().convert(go, dest)


class VirtConverter(IGrammarConverter, IVisualRepresentation):
    def convert(self, go: GrammarObject, dest: Path) -> None:
        return super().convert(go, dest)

    def to_visual(self, dest: Path) -> None:
        pass


class UmlConverter(IGrammarConverter, IVisualRepresentation):
    def convert(self, go: GrammarObject, dest: Path) -> None:
        return super().convert(go, dest)

    def to_visual(self, dest: Path) -> None:
        pass
