"""Точка запуска приложения «Система учета концертных выступлений».

Загружает коллекции объектов предметной области,
запускает меню и сохраняет изменения в JSON-файлы.
"""

from src import storage
from src.menu import run_menu
from src.models import Concert, Performer, Program, Venue
from pathlib import Path

DATA = Path("data")
PERFORMERS_FILE: str = str(DATA.joinpath("performers.join"))
VENUES_FILE: str = str(DATA.joinpath("venues.json"))
PROGRAMS_FILE: str = str(DATA.joinpath("programs.json"))
CONCERTS_FILE: str = str(DATA.joinpath("concerts.json"))


def load_all_data() -> tuple[
    list[Performer], list[Venue], list[Program], list[Concert]
]:
    """Загрузить все данные проекта и создать объекты."""
    performers: list[Performer] = storage.load_performers(PERFORMERS_FILE)
    venues: list[Venue] = storage.load_venues(VENUES_FILE)
    programs: list[Program] = storage.load_programs(PROGRAMS_FILE)
    concerts: list[Concert] = storage.load_concerts(
        CONCERTS_FILE, performers, venues, programs)
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
    data: tuple[list[Performer], list[Venue],
                list[Program], list[Concert]] = load_all_data()
    run_menu(data)
    save_all_data(*data)


if __name__ == "__main__":  # pragma: no cover
    main()
