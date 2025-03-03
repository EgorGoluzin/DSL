from DSLTools.models import (IScanner, IAfterscanner, GrammarObject, Token)
import re
from typing import List


class DefaultScanner(IScanner):
    def __init__(self, grammar: GrammarObject):
        self.grammar = grammar
        self.patterns = []

        # Сначала добавляем ключевые слова как литералы
        for key_type, key_value in self.grammar.keys:
            # Экранируем специальные символы в ключах
            pattern = re.escape(key_value)
            self.patterns.append(
                (key_type, re.compile(f'{pattern}'))
            )

        # Затем добавляем терминалы по убыванию специфичности
        # ordered_terminals = self.grammar.terminals.values()
        ordered_terminals = sorted(
            self.grammar.terminals.values(),
            key=lambda t: len(t.pattern),
            reverse=True
        )
        for terminal in ordered_terminals:
            self.patterns.append(
                (terminal.name, re.compile(f'{terminal.pattern}'))
            )

    def tokenize(self, input_str: str) -> List[Token]:
        tokens = []
        position = 0
        line_num = 1
        column = 1
        input_len = len(input_str)

        while position < input_len:
            # Пропускаем пробелы
            if input_str[position].isspace():
                if input_str[position] == '\n':
                    line_num += 1
                    column = 1
                else:
                    column += 1
                position += 1
                continue

            match = None
            for token_type, pattern in self.patterns:
                if (regex_match := pattern.match(input_str, position)) is not None:
                    value = regex_match.group()
                    token = Token(
                        token_type=token_type,
                        value=value,
                        line=line_num,
                        column=column
                    )
                    tokens.append(token)

                    # Обновляем позицию
                    length = len(value)
                    position += length if length > 0 else 1
                    column += length
                    break
            else:
                # Если не нашли совпадений

                context = input_str[position:position + 20]
                raise SyntaxError(
                    f"Unexpected token at line {line_num}, column {column}\n"
                    f"Context: {context}..."
                )

        return tokens
