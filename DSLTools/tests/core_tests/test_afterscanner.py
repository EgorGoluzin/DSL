import unittest
from DSLTools.models import GrammarObject, Token, Terminal
from DSLTools.core.scanning import DefaultAfterScanner  # Замените на ваш модуль


class TestDefaultAfterScanner(unittest.TestCase):
    def setUp(self):
        # Создаем объект GrammarObject для тестов
        self.grammar = GrammarObject(axiom="EXPRESSIONS", non_terminals=["EXPRESSIONS", "EXPRESSION", "TERM"])
        # Ключевые слова
        self.grammar.keys = [
            ("operation", "+"),
            ("operation", "*"),
            ("operation", "+="),
            ("terminator", ","),
        ]

        # Терминалы
        self.grammar.terminals = {
            "number": Terminal(name="number", pattern=r"[1-9]\d*"),
            "operation": Terminal(name="operation", pattern=r"[\+\*=]"),
            "terminator": Terminal(name="terminator", pattern=r","),
        }

        # Инициализация AfterScanner
        self.afterscanner = DefaultAfterScanner(self.grammar)

    def test_compute_attributes_number(self):
        """Проверка вычисления атрибутов для чисел."""
        tokens = [Token(token_type="number", value="42", line=1, column=1)]
        processed_tokens = self.afterscanner.process(tokens)
        self.assertEqual(processed_tokens[0].value, 42)  # Значение должно быть числом

    def test_replace_terminal_with_keyword(self):
        """Проверка замены терминалов на ключевые слова."""
        tokens = [Token(token_type="operation", value="+", line=1, column=1)]
        processed_tokens = self.afterscanner.process(tokens)
        self.assertEqual(processed_tokens[0].token_type, "operation")  # Тип должен быть "operation"

    def test_split_compound_operator(self):
        """Проверка разделения составных операторов."""
        tokens = [Token(token_type="operation", value="+=", line=1, column=1)]
        processed_tokens = self.afterscanner.process(tokens)
        self.assertEqual(len(processed_tokens), 2)  # Должно быть два токена
        self.assertEqual(processed_tokens[0].value, "+")  # Первый токен: "+"
        self.assertEqual(processed_tokens[1].value, "=")  # Второй токен: "="

    def test_complex_expression(self):
        """Проверка обработки сложного выражения."""
        tokens = [
            Token(token_type="number", value="42", line=1, column=1),
            Token(token_type="operation", value="+=", line=1, column=4),
            Token(token_type="number", value="10", line=1, column=7),
            Token(token_type="terminator", value=",", line=1, column=10),
        ]
        processed_tokens = self.afterscanner.process(tokens)

        # Ожидаемые токены
        expected_tokens = [
            Token(token_type="number", value=42, line=1, column=1),
            Token(token_type="operation", value="+", line=1, column=4),
            Token(token_type="operation", value="=", line=1, column=5),
            Token(token_type="number", value=10, line=1, column=7),
            Token(token_type="terminator", value=",", line=1, column=10),
        ]
        self.assertEqual(processed_tokens, expected_tokens)
        self.assertEqual(len(processed_tokens), len(expected_tokens))
        for processed, expected in zip(processed_tokens, expected_tokens):
            self.assertEqual(processed.token_type, expected.token_type)
            self.assertEqual(processed.value, expected.value)
            self.assertEqual(processed.line, expected.line)
            self.assertEqual(processed.column, expected.column)

    def test_no_changes_for_non_matching_tokens(self):
        """Проверка, что токены, не требующие изменений, остаются без изменений."""
        tokens = [Token(token_type="terminator", value=",", line=1, column=1)]
        processed_tokens = self.afterscanner.process(tokens)
        self.assertEqual(processed_tokens[0].value, ",")  # Значение должно остаться строкой

    def test_empty_input(self):
        """Проверка обработки пустого списка токенов."""
        tokens = []
        processed_tokens = self.afterscanner.process(tokens)
        self.assertEqual(len(processed_tokens), 0)


if __name__ == "__main__":
    unittest.main()