from DSLTools.models import (IScanner, IAfterscanner, GrammarObject, Token)
import re
from typing import List


class DefaultScanner(IScanner):
    def __init__(self, grammar: GrammarObject):
        self.grammar = grammar
        self.patterns = []
        self.terminal_list = [term.name for term in grammar.terminals.values()]
        self.key_list = [value for key, value in grammar.keys]
        print(self.key_list)
        # Сначала добавляем ключевые слова как литералы
        for key_type, key_value in self.grammar.keys:
            # Экранируем специальные символы в ключах
            pattern = re.escape(key_value)
            self.patterns.append(
                (key_value, re.compile(f'{pattern}'))
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
                    print(token_type)
                    value = regex_match.group()
                    if token_type in self.terminal_list:
                        token = Token(
                            token_type=Token.Type.TERMINAL,
                            value=value,
                            line=line_num,
                            column=column
                        )
                        token.terminalType = token_type
                    elif token_type in self.key_list:
                        token = Token(
                            token_type=Token.Type.KEY,
                            value=value,
                            line=line_num,
                            column=column
                        )
                        token.str = token_type
                    else:
                        raise "Unexpected token!"
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


class DefaultAfterScanner(IAfterscanner):
    def __init__(self, grammar: GrammarObject):
        self.grammar = grammar
        self.patterns = []

        # Создаем шаблоны для разделения составных операторов
        self._init_patterns()

    def _init_patterns(self):
        """Инициализация шаблонов для разделения составных операторов."""
        # Пример: если есть ключевые слова "+=" и "+", то "+=" должно обрабатываться первым
        self.patterns = sorted(
            [(key_value, key_type) for key_type, key_value in self.grammar.keys],
            key=lambda x: len(x[0]),
            reverse=True  # Сначала более длинные ключевые слова
        )

    def process(self, tokens: List[Token]) -> List[Token]:
        """Обработка токенов после сканирования."""
        processed_tokens = []

        for token in tokens:
            # 1. Вычисление атрибутов лексем
            self._compute_attributes(token)

            # 2. Замена терминалов на ключевые слова
            self._replace_terminal_with_keyword(token)

            # 3. Разделение составных операторов
            self._split_compound_tokens(token, processed_tokens)

        return processed_tokens

    def _compute_attributes(self, token: Token):
        """Вычисление атрибутов токена."""
        if token.token_type == "number":
            # Преобразуем значение в число
            try:
                token.value = int(token.value)
            except ValueError:
                pass  # Оставляем как строку, если не удалось преобразовать

    def _replace_terminal_with_keyword(self, token: Token):
        """Замена терминалов на ключевые слова, если они совпадают."""
        for key_value, key_type in self.grammar.keys:
            if token.value == key_value:
                token.token_type = key_type
                break

    def _split_compound_tokens(self, token: Token, processed_tokens: List[Token]):
        """Разделение составных токенов на части."""
        if token.token_type == "operation":
            # Пример: разделение "+=" на "+" и "="
            remaining_value = token.value
            while remaining_value:
                matched = False
                for key_value, key_type in self.patterns:
                    if remaining_value.startswith(key_value):
                        # Создаем новый токен для части значения
                        new_token = Token(
                            token_type=key_type,
                            value=key_value,
                            line=token.line,
                            column=token.column
                        )
                        processed_tokens.append(new_token)
                        remaining_value = remaining_value[len(key_value):]
                        token.column += len(key_value)  # Обновляем позицию
                        matched = True
                        break
                if not matched:
                    # Если не удалось разделить, добавляем оставшуюся часть как есть
                    new_token = Token(
                        token_type=token.token_type,
                        value=remaining_value,
                        line=token.line,
                        column=token.column
                    )
                    processed_tokens.append(new_token)
                    break
        else:
            # Если токен не требует разделения, добавляем его как есть
            processed_tokens.append(token)
