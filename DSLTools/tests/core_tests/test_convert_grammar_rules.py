import unittest
from typing import Dict
from pathlib import Path
from DSLTools.core.wirth_diagram_generation import generate_dot
from DSLTools.models import (
    Rule, RuleElement, ElementType, Diagram
)
from DSLTools.core.rule_wirth_converter import convert_rules_to_diagrams
from DSLTools.utils.file_ops import generate_file
from DSLTools.utils.wirth_render import render_dot_to_png
from settings import settings


# Тестовые классы
class TestRuleConverter(unittest.TestCase):
    def setUp(self):
        self.project_path = settings.PROJECT_ROOT
        self.example_test_path = Path(self.project_path, r"tests\example_tests\convert_grammar_rules")
        pass

    def test_convertion_group(self):
        """ПРОСТОЙ ТЕСТ ДЛЯ ГРУППЫ. Expression ::= {'$' '^' '$'};"""
        # Arrange
        rule_name = 'Expression'
        Expression = Rule(lpart=rule_name,
                          rpart=RuleElement(type=ElementType.SEQUENCE,
                                            value=[RuleElement(
                                                type=ElementType.GROUP,
                                                value=[RuleElement(value="$", type=ElementType.KEYWORD),
                                                       RuleElement(value="^", type=ElementType.KEYWORD),
                                                       RuleElement(value="G", type=ElementType.KEYWORD)])]))
        rules_to_test = {rule_name: Expression}
        # Act
        result = convert_rules_to_diagrams(rules=rules_to_test)
        # Создаем .gv файл Expression
        cur_path = Path(self.example_test_path, fr"wirth\{rule_name}.gv")
        generate_file(generate_dot(result["Expression"]), cur_path)
        render_dot_to_png(cur_path, fr"{self.example_test_path}\wirthpng")
        # Assert # TODO: Написать нормальный assert
        self.assertIsNotNone(result)

    def test_convertion_alternative(self):
        """ПРОСТОЙ ТЕСТ ДЛЯ ГРУППЫ. Expression ::= {'$' '^' '$'};"""
        # Arrange
        rule_name = 'ExpressionAlt'
        Expression = Rule(lpart=rule_name,
                          rpart=RuleElement(type=ElementType.SEQUENCE,
                                            value=[RuleElement(
                                                type=ElementType.ALTERNATIVE,
                                                value=[RuleElement(value=[RuleElement(value="$",
                                                                                      type=ElementType.KEYWORD),
                                                                          RuleElement(value="$",
                                                                                      type=ElementType.KEYWORD),
                                                                          ], type=ElementType.SEQUENCE),
                                                       RuleElement(value="^", type=ElementType.KEYWORD)])]))
        rules_to_test = {rule_name: Expression}
        # Act
        result = convert_rules_to_diagrams(rules=rules_to_test)
        # Создаем .gv файл Expression
        cur_path = Path(self.example_test_path, fr"wirth\{rule_name}.gv")
        generate_file(generate_dot(result[rule_name]), cur_path)
        render_dot_to_png(cur_path, fr"{self.example_test_path}\wirthpng")
        # Assert # TODO: Написать нормальный assert
        self.assertIsNotNone(result)

    def test_convertion_optional(self):
        """Тест для опционального выражения Expression ::= {'$' ['^'] '$'};"""
        # Arrange
        rule_name = 'OptionalTest'
        Expression = Rule(lpart=rule_name,
                          rpart=RuleElement(type=ElementType.SEQUENCE,
                                            value=[
                                                RuleElement(
                                                    type=ElementType.GROUP,
                                                    value=[RuleElement(value="$", type=ElementType.KEYWORD),
                                                           RuleElement(type=ElementType.OPTIONAL,
                                                                       value=[
                                                                           RuleElement(value="OP1",
                                                                                       type=ElementType.KEYWORD),
                                                                           RuleElement(value="OP2",
                                                                                       type=ElementType.KEYWORD)
                                                                       ], separator=None),
                                                           RuleElement(value="T1", type=ElementType.KEYWORD),
                                                           RuleElement(type=ElementType.OPTIONAL,
                                                                       value=[
                                                                           RuleElement(value="OP3",
                                                                                       type=ElementType.KEYWORD),
                                                                           RuleElement(value="OP4",
                                                                                       type=ElementType.KEYWORD)
                                                                       ], separator=None),
                                                           RuleElement(value="G", type=ElementType.KEYWORD)]),
                                                RuleElement(type=ElementType.OPTIONAL,
                                                            value=[
                                                                RuleElement(value="OP1", type=ElementType.KEYWORD),
                                                                RuleElement(value="OP2",
                                                                            type=ElementType.KEYWORD)
                                                            ], separator=None)]))
        rules_to_test = {rule_name: Expression}
        # Act
        result = convert_rules_to_diagrams(rules=rules_to_test)
        # Создаем .gv файл Expression
        cur_path = Path(self.example_test_path, fr"wirth\{rule_name}.gv")
        generate_file(generate_dot(result[rule_name]), cur_path)
        render_dot_to_png(cur_path, fr"{self.example_test_path}\wirthpng")
        # Assert # TODO: Написать нормальный assert
        self.assertIsNotNone(result)

    def test_convert_conditional_rule(self):
        """Тест для правила с группами и опциональными элементами (пока это выражение невалидно читается):
        Conditional ::= 'IF' Expression 'THEN' Block [ { 'ELSEIF' Expression 'THEN' Block } ] [ 'ELSE' Block ] 'END_IF'; """
        # Arrange
        rule_name = "Conditional"
        # conditional_rule = Rule(
        #     lpart=rule_name,
        #     rpart=RuleElement(
        #         type=ElementType.SEQUENCE,
        #         value=[
        #             # 'IF' Expression 'THEN' Block
        #             RuleElement(type=ElementType.KEYWORD, value="IF"),
        #             RuleElement(type=ElementType.NONTERMINAL, value="Expression"),
        #             RuleElement(type=ElementType.KEYWORD, value="THEN"),
        #             RuleElement(type=ElementType.NONTERMINAL, value="Block"),
        #
        #             # [ { 'ELSEIF' Expression 'THEN' Block } ]
        #             RuleElement(
        #                 type=ElementType.OPTIONAL,
        #                 value=[
        #                     RuleElement(
        #                         type=ElementType.GROUP,
        #                         value=[
        #                             RuleElement(type=ElementType.KEYWORD, value="ELSEIF"),
        #                             RuleElement(type=ElementType.NONTERMINAL, value="Expression"),
        #                             RuleElement(type=ElementType.KEYWORD, value="THEN"),
        #                             RuleElement(type=ElementType.NONTERMINAL, value="Block")
        #                         ],
        #                         separator=None
        #                     )
        #                 ]
        #             ),
        #             RuleElement(type=ElementType.KEYWORD, value="TODEL"),
        #             # [ 'ELSE' Block ]
        #             RuleElement(
        #                 type=ElementType.OPTIONAL,
        #                 value=[
        #                     RuleElement(type=ElementType.KEYWORD, value="ELSE"),
        #                     RuleElement(type=ElementType.NONTERMINAL, value="Block")
        #                 ]
        #             ),
        #
        #             # 'END_IF'
        #             RuleElement(type=ElementType.KEYWORD, value="END_IF")
        #         ]
        #     )
        # )
        #
        # rules_to_test = {rule_name: conditional_rule}
        #
        # # Act
        # result = convert_rules_to_diagrams(rules=rules_to_test)
        cur_path = Path(self.example_test_path, fr"wirth\{rule_name}.gv")
        # Создаем .gv файл Conditional
        # generate_file(
        #     generate_dot(result[rule_name]),
        #     cur_path
        # )
        render_dot_to_png(cur_path, fr"{self.example_test_path}\wirthpng")
        # Assert
        # self.assertIsNotNone(result)
        # self.assertIn(rule_name, result)
        #
        # # Дополнительные проверки структуры диаграммы
        # diagram = result[rule_name]
        # self.assertEqual(len(diagram.start.next_nodes), 5)  # IF + 4 основных элемента
        # self.assertTrue(any(n.node_type == "optional" for n in diagram.nodes.values()))
