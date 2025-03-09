import unittest
from DSLTools.models import GrammarObject, Token, Terminal
from DSLTools.core.scanning import DefaultScanner  # Замените на ваш модуль


class TestDefaultScanner(unittest.TestCase):
    def setUp(self):
        self.grammar = GrammarObject(axiom="EXPRESSIONS", non_terminals=["EXPRESSIONS"])
        # Терминалы
        self.grammar.terminals = {
            "number": Terminal(name="number", pattern=r"[1-9]\d*"),
            "operation": Terminal(name="operation", pattern=r"[\+\*]"),
            "terminator": Terminal(name="terminator", pattern=r","),
        }

        # Ключевые слова
        self.grammar.keys = [
            ("operation", "+"),
            ("operation", "*"),
            ("terminator", ","),
        ]

        # Инициализация сканера
        self.scanner = DefaultScanner(self.grammar)

    def test_tokenize_numbers(self):
        input_str = "42 123"
        expected_tokens = [
            Token(token_type="number", value="42", line=1, column=1),
            Token(token_type="number", value="123", line=1, column=4),
        ]
        result = self.scanner.tokenize(input_str)
        self.assertEqual(result, expected_tokens)

    def test_tokenize_operations(self):
        input_str = "+ *"
        expected_tokens = [
            Token(token_type="operation", value="+", line=1, column=1),
            Token(token_type="operation", value="*", line=1, column=3),
        ]
        result = self.scanner.tokenize(input_str)
        self.assertEqual(result, expected_tokens)

    def test_tokenize_terminator(self):
        input_str = ","
        expected_tokens = [
            Token(token_type="terminator", value=",", line=1, column=1),
        ]
        result = self.scanner.tokenize(input_str)
        self.assertEqual(result, expected_tokens)

    def test_tokenize_complex_expression(self):
        input_str = "42 + 123 * 7,"
        expected_tokens = [
            Token(token_type="number", value="42", line=1, column=1),
            Token(token_type="operation", value="+", line=1, column=4),
            Token(token_type="number", value="123", line=1, column=6),
            Token(token_type="operation", value="*", line=1, column=10),
            Token(token_type="number", value="7", line=1, column=12),
            Token(token_type="terminator", value=",", line=1, column=13),
        ]
        result = self.scanner.tokenize(input_str)
        self.assertEqual(result, expected_tokens)

    def test_tokenize_invalid_input(self):
        input_str = "42 + abc"
        with self.assertRaises(SyntaxError) as context:
            self.scanner.tokenize(input_str)
        self.assertIn("Unexpected token", str(context.exception))

    def test_tokenize_with_whitespace(self):
        input_str = "  42  +  123  ,  "
        expected_tokens = [
            Token(token_type="number", value="42", line=1, column=3),
            Token(token_type="operation", value="+", line=1, column=6),
            Token(token_type="number", value="123", line=1, column=9),
            Token(token_type="terminator", value=",", line=1, column=13),
        ]
        result = self.scanner.tokenize(input_str)
        self.assertEqual(result, expected_tokens)

    def test_tokenize_multiline_input(self):
        input_str = "42\n+ 123\n,"
        expected_tokens = [
            Token(token_type="number", value="42", line=1, column=1),
            Token(token_type="operation", value="+", line=2, column=1),
            Token(token_type="number", value="123", line=2, column=3),
            Token(token_type="terminator", value=",", line=3, column=1),
        ]
        result = self.scanner.tokenize(input_str)
        self.assertEqual(result, expected_tokens)

    def test_tokenize_empty_input(self):
        input_str = ""
        result = self.scanner.tokenize(input_str)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
