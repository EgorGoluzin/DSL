import unittest
from unittest.mock import Mock, patch
from pathlib import Path
from DSLTools.models.interface import (
    IGrammarParser,
    IGrammarConverter,
    IVisualRepresentation,
    GrammarObject,
)


# Тестовые классы
class TestGrammarParser(unittest.TestCase):
    def setUp(self):
        # Mock MetaObject
        self.mock_meta = Mock()
        self.mock_meta.syntax = {
            "type": "test",
            "info": {
                "supportInfo": "test.sgi",
                "diagrams": "test_diagrams"
            }
        }
        self.mock_meta.debug_info_dir = "_debug"

    def test_parser_interface(self):
        """Тестирование контракта интерфейса IGrammarParser"""
        class ConcreteParser(IGrammarParser):
            def parse(self, meta_info):
                return GrammarObject([], [], {}, "")

        parser = ConcreteParser()
        result = parser.parse(self.mock_meta)
        self.assertIsInstance(result, GrammarObject)