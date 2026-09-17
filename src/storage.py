"""Сохранение и загрузка данных проекта в JSON-файлах.

JSON используется для хранения данных, объектная модель — для работы
приложения. Загрузка преобразует данные JSON в объекты, сохранение —
объекты обратно в данные JSON.
"""

import json
from pathlib import Path

from src.models import Concert, Performer, Program, Venue


def _load_json(filename: str) -> list[dict]:
    """Прочитать данные из JSON-файла.

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


def _save_json(filename: str, data: list[dict]) -> None:
    """Записать данные в JSON-файл через контекстный менеджер."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.write("\n")


def load_performers(filename: str) -> list[Performer]:
    """Загрузить исполнителей из JSON-файла и создать объекты."""
    return [Performer.from_data(d) for d in _load_json(filename)]


def save_performers(filename: str, performers: list[Performer]) -> None:
    """Сохранить исполнителей в JSON-файл."""
    _save_json(filename, [p.to_data() for p in performers])


def load_venues(filename: str) -> list[Venue]:
    """Загрузить площадки из JSON-файла и создать объекты."""
    return [Venue.from_data(d) for d in _load_json(filename)]


def save_venues(filename: str, venues: list[Venue]) -> None:
    """Сохранить площадки в JSON-файл."""
    _save_json(filename, [v.to_data() for v in venues])


def load_programs(filename: str) -> list[Program]:
    """Загрузить программы из JSON-файла и создать объекты."""
    return [Program.from_data(d) for d in _load_json(filename)]


def save_programs(filename: str, programs: list[Program]) -> None:
    """Сохранить программы в JSON-файл."""
    _save_json(filename, [p.to_data() for p in programs])


def load_concerts(
    filename: str,
    performers: list[Performer],
    venues: list[Venue],
    programs: list[Program],
) -> list[Concert]:
    """Загрузить концерты из JSON-файла, восстановив связи с объектами.

    Бронирования с неизвестными идентификаторами связанных объектов
    не создаются.
    """
    concerts = []
    for data in _load_json(filename):
        concert = Concert.from_data(data, performers, venues, programs)
        if concert is not None:
            concerts.append(concert)
    return concerts


def save_concerts(filename: str, concerts: list[Concert]) -> None:
    """Сохранить концерты в JSON-файл."""
    _save_json(filename, [c.to_data() for c in concerts])
