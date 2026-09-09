"""Сохранение и загрузка данных проекта в JSON-файлах."""

import json
from pathlib import Path


def load_data(filename: str) -> list[dict]:
    """Загрузить данные из JSON-файла.

    При отсутствии файла или некорректном JSON возвращает пустой список,
    программа не завершается аварийно.
    """
    path = Path(filename)
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []
    return data


def save_data(filename: str, data: list[dict]) -> None:
    """Сохранить данные в JSON-файл через контекстный менеджер."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.write("\n")
