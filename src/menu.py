"""Консольное меню приложения «Система учета концертных выступлений»."""

from datetime import date

from src.models import Concert, Venue
from src.models.concerts import (
    add_concert,
    cancel_concert,
    find_concerts,
    get_concerts_statistics,
    is_venue_available,
    sort_concerts_by_date,
)
from src.models.performers import get_performer_by_id
from src.models.programs import get_program_by_id
from src.models.venues import (
    filter_venues_by_capacity,
    find_venues,
    get_venue_by_id,
    sort_venues_by_capacity,
)
from src.utils import input_date, input_int

MENU = """=== Система учета концертных выступлений ===

1. Показать концерты
2. Найти концерт по названию
3. Показать площадки
4. Найти площадку по названию
5. Отобрать площадки по вместимости
6. Проверить доступность площадки на дату
7. Добавить концерт
8. Отменить концерт
9. Статистика концертов
0. Выход"""


def show_concerts(concerts: list[Concert]) -> None:
    """Вывести список концертов со связанными объектами."""
    if not concerts:
        print("Концерты не найдены")
        return
    today = date.today()
    for concert in sort_concerts_by_date(concerts):
        print(f"{concert.id}. {concert.title}")
        print(f"   Дата: {concert.date} ({concert.get_status(today)})")
        print(f"   Исполнитель: {concert.performer.name}")
        print(f"   Площадка: {concert.venue.name}, {concert.venue.city}")
        print(f"   Программа: {concert.program.name}")
        print(f"   Ожидается зрителей: {concert.expected_guests}")
        print()


def show_venues(venues: list[Venue]) -> None:
    """Вывести список площадок."""
    if not venues:
        print("Площадки не найдены")
        return
    for venue in sort_venues_by_capacity(venues):
        print(f"{venue.id}. {venue}")


def menu_show_concerts(data: tuple[list, ...]) -> None:
    """Пункт меню: показать все концерты."""
    show_concerts(data[3])


def menu_find_concert(data: tuple[list, ...]) -> None:
    """Пункт меню: найти концерт по подстроке названия."""
    query = input("Название концерта: ")
    show_concerts(find_concerts(data[3], query))


def menu_show_venues(data: tuple[list, ...]) -> None:
    """Пункт меню: показать все площадки."""
    show_venues(data[1])


def menu_find_venue(data: tuple[list, ...]) -> None:
    """Пункт меню: найти площадку по подстроке названия."""
    query = input("Название площадки: ")
    show_venues(find_venues(data[1], query))


def menu_filter_venues(data: tuple[list, ...]) -> None:
    """Пункт меню: отобрать площадки по минимальной вместимости."""
    min_capacity = input_int("Минимальная вместимость: ")
    show_venues(filter_venues_by_capacity(data[1], min_capacity))


def menu_check_venue(data: tuple[list, ...]) -> None:
    """Пункт меню: проверить доступность площадки на дату."""
    venue_id = input_int("Идентификатор площадки: ")
    check_date = input_date("Дата (ДД.ММ.ГГГГ): ")
    if is_venue_available(data[3], venue_id, check_date):
        print("Площадка свободна")
    else:
        print("Площадка занята")


def menu_add_concert(data: tuple[list, ...]) -> None:
    """Пункт меню: добавить концерт."""
    performers, venues, programs, concerts = data
    title = input("Название концерта: ")
    performer_id = input_int("Идентификатор исполнителя: ")
    performer = get_performer_by_id(performers, performer_id)
    if performer is None:
        print("Ошибка: исполнитель не найден")
        return
    venue_id = input_int("Идентификатор площадки: ")
    venue = get_venue_by_id(venues, venue_id)
    if venue is None:
        print("Ошибка: площадка не найдена")
        return
    program_id = input_int("Идентификатор программы: ")
    program = get_program_by_id(programs, program_id)
    if program is None:
        print("Ошибка: программа не найдена")
        return
    concert_date = input_date("Дата (ДД.ММ.ГГГГ): ")
    expected_guests = input_int("Ожидаемое число зрителей: ")
    if not is_venue_available(concerts, venue.id, concert_date):
        print("Ошибка: площадка занята на эту дату")
        return
    if not venue.is_suitable_for(expected_guests):
        print("Ошибка: площадка не вмещает всех зрителей")
        return
    add_concert(
        concerts,
        title,
        performer,
        venue,
        program,
        concert_date,
        expected_guests,
        2000.0,
    )
    print("Концерт добавлен")


def menu_cancel_concert(data: tuple[list, ...]) -> None:
    """Пункт меню: отменить концерт."""
    concert_id = input_int("Идентификатор концерта: ")
    if cancel_concert(data[3], concert_id):
        print("Концерт отменен")
    else:
        print("Ошибка: концерт не найден")


def menu_statistics(data: tuple[list, ...]) -> None:
    """Пункт меню: вывести статистику концертов."""
    statistics = get_concerts_statistics(data[3], date.today())
    print(f"Запланировано концертов: {statistics['planned']}")
    print(f"Прошедших концертов: {statistics['past']}")
    print(f"Отменено концертов: {statistics['cancelled']}")
    print(f"Ожидается зрителей: {statistics['total_guests']}")


ACTIONS = {
    "1": menu_show_concerts,
    "2": menu_find_concert,
    "3": menu_show_venues,
    "4": menu_find_venue,
    "5": menu_filter_venues,
    "6": menu_check_venue,
    "7": menu_add_concert,
    "8": menu_cancel_concert,
    "9": menu_statistics,
}


def run_menu(data: tuple[list, ...]) -> None:
    """Основной цикл меню приложения."""
    while True:
        print(MENU)
        choice = input("Выберите действие: ")
        if choice == "0":
            break
        action = ACTIONS.get(choice)
        if action is None:
            print("Неверное действие")
            continue
        action(data)
