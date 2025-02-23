import unittest
import tempfile
from pathlib import Path
from DSLTools.core.grammar_parsers import VirtParser
from DSLTools.models.parse import Rule, Iteration

class TestVirtParser(unittest.TestCase):
    def setUp(self):
        self.test_data = """
        digraph EXPRESSION {
            start [label=EXPRESSION shape=plaintext]
            A [label=TERM shape=box]
            B [label="+" shape=oval]
            end [label="" shape=point]
            start -> A
            A -> B
            B -> A
            A -> end
        }
        """

    def test_simple_expression(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Создаем тестовую диаграмму
            diagram_path = Path(tmpdir) / "test.gv"
            diagram_path.write_text(self.test_data)

            # Парсим
            parser = VirtParser(tmpdir)
            rules = parser.parse()

            # Проверяем результаты
            self.assertIn("EXPRESSION", rules)
            expr_rule = rules["EXPRESSION"]
            self.assertEqual(len(expr_rule.alternatives), 1)

            # Проверяем наличие итерации
            self.assertIsInstance(expr_rule.alternatives[0][1], Iteration)

            # Проверяем терминалы
            self.assertEqual(expr_rule.alternatives[0][1].elements[0].value, "+")


# class TestDSLInfoGenerator(unittest.TestCase):
#     def test_generation(self):
#         metadata = {
#             'terminals': {'PLUS': '+'},
#             'keys': ['+'],
#             'nonterminals': ['EXPRESSION'],
#             'axiom': 'EXPRESSION'
#         }
#
#         rules = {
#             'EXPRESSION': Rule('EXPRESSION')
#         }
#
#         generator = DSLInfoGenerator(metadata, rules)
#         with tempfile.TemporaryDirectory() as tmpdir:
#             output_path = Path(tmpdir) / "dsl_info.py"
#             generator.generate("templates/dsl_info.template", output_path)
#
#             # Проверяем что файл создан
#             self.assertTrue(output_path.exists())
#
#             # Проверяем синтаксис
#             try:
#                 with open(output_path) as f:
#                     exec(f.read(), {})
#             except Exception as e:
#                 self.fail(f"Generated code is invalid: {e}")