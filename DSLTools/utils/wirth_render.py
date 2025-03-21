import pathlib

from graphviz import Source


def render_dot_to_png(dot_file_path: str, output_dir: str) -> None:
    """
    Рендерит DOT-файл в PNG изображение.

    Args:
        dot_file_path: Путь к исходному .gv файлу
        output_dir: Директория для сохранения PNG
    """
    try:
        # Создаем директорию, если её нет
        pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Генерируем PNG
        s = Source.from_file(dot_file_path, format="png")
        output_path = pathlib.Path(output_dir) / pathlib.Path(dot_file_path).stem
        s.render(filename=output_path, cleanup=True)

    except Exception as e:
        print(f"Ошибка рендеринга {dot_file_path}: {str(e)}")
