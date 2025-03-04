import shutil
import os
from pathlib import Path
import json
def load_config(json_path):
    with open(json_path) as f:
        return json.load(f)
def copy_template(src_dir, dest_dir, filename):
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy(src_dir / filename, dest_dir / filename)


def generate_file(content, output_path):
    os.makedirs(output_path.parent, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)


def validate_paths(project_path: Path, input_path: Path, is_dir: bool) -> Path:
    """
    Валидирует путь и преобразует его в абсолютный, если он относительный.
    :param project_path: Путь к папке проекта
    :param input_path: Путь для валидации.
    :param is_dir: Флаг, указывающий, должен ли путь быть директорией (True) или файлом (False).
    :return: Абсолютный путь.
    :raises ValueError: Если путь не валидный или не соответствует ожидаемому типу (директория/файл).
    """
    # Если путь относительный, преобразуем его в абсолютный относительно PROJECT_ROOT
    if not input_path.is_absolute():
        input_path = project_path / input_path

    # Проверяем, существует ли путь
    if not input_path.exists():
        raise ValueError(f"Путь {input_path} не существует.")

    # Проверяем, является ли путь директорией или файлом в зависимости от is_dir
    if is_dir:
        if not input_path.is_dir():
            raise ValueError(f"Путь {input_path} не является директорией.")
    else:
        if not input_path.is_file():
            raise ValueError(f"Путь {input_path} не является файлом.")

    return input_path
