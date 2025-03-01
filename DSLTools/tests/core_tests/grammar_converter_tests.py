import unittest
from unittest.mock import Mock, patch
from pathlib import Path
from DSLTools.models.interface import (
    IGrammarParser,
    IGrammarConverter,
    IVisualRepresentation,
    GrammarObject,
)
from DSLTools.models.parse import (Rule,
                                   Iteration,
                                   Terminal)
from DSLTools.core.converters import RBNFConverter, VirtConverter, UmlConverter


class TestRBNFConverter(unittest.TestCase):
    def setUp(self):
        self.converter = RBNFConverter()
        self.test_rule = Rule(
            "Expression",
            [
                [Terminal("number"), Iteration([Terminal("+"), Terminal("number")], separator="+")],
                [Terminal("string")]
            ]
        )

    def test_generate_method(self):
        """Тестирование генерации RBNF-правил"""
        expected = (
            "Expression ::= number { + number # + } .\n"
            "    | string ."
        )
        result = RBNFConverter.generate(self.test_rule)
        self.assertEqual(result, expected)

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_convert_method(self, mock_open):
        """Тестирование сохранения в файл"""
        go = GrammarObject(
            terminals=["number", "string"],
            non_terminals=["Expression"],
            rules={"Expression": self.test_rule},
            axiom="Expression"
        )

        dest = Path("test_output.rbnf")
        self.converter.convert(go, dest)

        mock_open.assert_called_once_with(dest, "w", encoding="utf-8")


class TestVirtConverter(unittest.TestCase):
    def setUp(self):
        self.converter = VirtConverter()
        self.test_go = GrammarObject(
            terminals=["+", "number"],
            non_terminals=["Expression"],
            rules={},
            axiom="Expression"
        )

    @patch("pathlib.Path.mkdir")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_convert_and_visual(self, mock_open, mock_mkdir):
        """Интеграционный тест конвертера Virt"""
        # Тестирование конвертации
        dest = Path("test_output/virt")
        self.converter.convert(self.test_go, dest)

        # Тестирование визуализации
        self.converter.to_visual(dest)

        # Проверка создания файлов
        mock_mkdir.assert_called()
        mock_open.assert_called()


class TestUmlConverter(unittest.TestCase):
    @patch("plantuml.PlantUML")
    def test_visualization(self, mock_plantuml):
        """Тестирование генерации UML"""
        converter = UmlConverter()
        dest = Path("test_diagram.puml")

        converter.to_visual(dest)

        mock_plantuml.assert_called_once()
        mock_plantuml.return_value.processes.assert_called()
