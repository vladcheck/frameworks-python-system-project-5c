"""Точка запуска приложения «Система учета концертных выступлений».

Загружает коллекции объектов предметной области,
запускает меню и сохраняет изменения в JSON-файлы.
"""

import storage
from menu import run_menu
from models import Concert, Performer, Program, Venue

DATA_DIR = "data/"
PERFORMERS_FILE = DATA_DIR + "performers.json"
VENUES_FILE = DATA_DIR + "venues.json"
PROGRAMS_FILE = DATA_DIR + "programs.json"
CONCERTS_FILE = DATA_DIR + "concerts.json"


def load_all_data() -> tuple[
    list[Performer], list[Venue], list[Program], list[Concert]
]:
    """Загрузить все данные проекта и создать объекты."""
    performers = storage.load_performers(PERFORMERS_FILE)
    venues = storage.load_venues(VENUES_FILE)
    programs = storage.load_programs(PROGRAMS_FILE)
    concerts = storage.load_concerts(CONCERTS_FILE, performers, venues, programs)
    return performers, venues, programs, concerts


def save_all_data(
    performers: list[Performer],
    venues: list[Venue],
    programs: list[Program],
    concerts: list[Concert],
) -> None:
    """Сохранить все коллекции объектов в JSON-файлы."""
    storage.save_performers(PERFORMERS_FILE, performers)
    storage.save_venues(VENUES_FILE, venues)
    storage.save_programs(PROGRAMS_FILE, programs)
    storage.save_concerts(CONCERTS_FILE, concerts)


def main() -> None:
    """Точка входа: загрузка данных, меню, сохранение."""
    data = load_all_data()
    run_menu(data)
    save_all_data(*data)


if __name__ == "__main__":
    main()
