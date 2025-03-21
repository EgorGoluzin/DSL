import pathlib
from dotenv import load_dotenv
from DSLTools.core.scanning import DefaultScanner
from DSLTools.core.tools import get_parser
from DSLTools.models import MetaObject
from DSLTools.utils.cli import parse_arguments
from DSLTools.utils.file_ops import validate_paths, load_config
from settings import settings as s

## History. Example from presentation
def sample_lexer():
    args = parse_arguments()
    json_path = validate_paths(project_path=s.PROJECT_ROOT, input_path=pathlib.Path(args.jsonFile), is_dir=False)
    config = load_config(json_path)
    mo = MetaObject(config)
    # Пример использования
    parser = get_parser(mo)
    # Шаг 3. Парсинг грамматики.
    grammarObject = parser.parse(mo)
    scanner = DefaultScanner(grammarObject) # Инициализация
    test_input = "7 + 2 + 3" # Пример для expression
    res = scanner.tokenize(test_input)
