import unittest
from typing import Dict

from DSLTools.models import (
    Rule, RuleElement, ElementType, Diagram
)
from DSLTools.core.rule_wirth_converter import convert_rules_to_diagrams


# Тестовые классы
class TestRuleConverter(unittest.TestCase):
    def setUp(self):
        pass

    def test_convertion_group(self):
        """ПРОСТОЙ ТЕСТ ДЛЯ ГРУППЫ. Expression ::= {'$' '^' '$'};"""
        # Fact
        Expression = Rule(lpart="Expression",
                          rpart=RuleElement(type=ElementType.SEQUENCE,
                                            value=[RuleElement(
                                                type=ElementType.GROUP,
                                                value=[RuleElement(value="$", type=ElementType.KEYWORD),
                                                       RuleElement(value="^", type=ElementType.KEYWORD),
                                                       RuleElement(value="$", type=ElementType.KEYWORD)])]))
        rules_to_test = {"Expression": Expression}
        # Act
        result = convert_rules_to_diagrams(rules=rules_to_test)

        # TODO: Дописать логику по конвертации к вирту

        # Assert
        self.assertIsNotNone(result)
