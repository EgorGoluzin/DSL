from DSLTools.models import (IGrammarConverter, IVisualRepresentation, Rule, GrammarObject)
from pathlib import Path


class RBNFConverter(IGrammarConverter):

    def convert(self, go: GrammarObject, dest: Path) -> None:
        lines = []
        return


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
