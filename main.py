"""Точка запуска приложения «Система учета концертных выступлений»."""

from datetime import date

import concerts
import performers
import programs
import storage
import venues
from utils import input_date, input_int

DATA_DIR = "data/"
PERFORMERS_FILE = DATA_DIR + "performers.json"
VENUES_FILE = DATA_DIR + "venues.json"
PROGRAMS_FILE = DATA_DIR + "programs.json"
CONCERTS_FILE = DATA_DIR + "concerts.json"

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


def show_concerts(
    concerts_list: list[dict],
    performers_list: list[dict],
    venues_list: list[dict],
    programs_list: list[dict],
) -> None:
    """Вывести список концертов с исполнителями и площадками."""
    if not concerts_list:
        print("Концерты не найдены")
        return
    today = date.today()
    for concert in concerts.sort_concerts_by_date(concerts_list):
        performer = performers.get_performer_by_id(
            performers_list, concert["performer_id"]
        )
        venue = venues.get_venue_by_id(venues_list, concert["venue_id"])
        program = programs.get_program_by_id(programs_list, concert["program_id"])
        performer_name = performer["name"] if performer else "неизвестен"
        if venue:
            venue_name = venue["name"] + ", " + venue["city"]
        else:
            venue_name = "неизвестна"
        program_name = program["name"] if program else "неизвестна"
        concert_day = date.fromisoformat(concert["date"])
        status = concerts.get_concert_status(concert_day, today)
        print(f"{concert['id']}. {concert['title']}")
        print(f"   Дата: {concert['date']} ({status})")
        print(f"   Исполнитель: {performer_name}")
        print(f"   Площадка: {venue_name}")
        print(f"   Программа: {program_name}")
        print(f"   Ожидается зрителей: {concert['expected_guests']}")
        print()


def show_venues(venues_list: list[dict]) -> None:
    """Вывести список площадок."""
    if not venues_list:
        print("Площадки не найдены")
        return
    for venue in venues.sort_venues_by_capacity(venues_list):
        print(
            f"{venue['id']}. {venue['name']}, {venue['city']} "
            f"({venue['capacity']} мест)"
        )


def load_all_data() -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """Загрузить все данные проекта из JSON-файлов."""
    return (
        storage.load_data(PERFORMERS_FILE),
        storage.load_data(VENUES_FILE),
        storage.load_data(PROGRAMS_FILE),
        storage.load_data(CONCERTS_FILE),
    )


def save_all_data(
    performers_list: list[dict],
    venues_list: list[dict],
    programs_list: list[dict],
    concerts_list: list[dict],
) -> None:
    """Сохранить все данные проекта в JSON-файлы."""
    storage.save_data(PERFORMERS_FILE, performers_list)
    storage.save_data(VENUES_FILE, venues_list)
    storage.save_data(PROGRAMS_FILE, programs_list)
    storage.save_data(CONCERTS_FILE, concerts_list)


def menu_show_concerts(data: tuple[list[dict], ...]) -> None:
    """Пункт меню: показать все концерты."""
    show_concerts(data[3], data[0], data[1], data[2])


def menu_find_concert(data: tuple[list[dict], ...]) -> None:
    """Пункт меню: найти концерт по подстроке названия."""
    query = input("Название концерта: ")
    found = concerts.find_concerts(data[3], query)
    show_concerts(found, data[0], data[1], data[2])


def menu_show_venues(data: tuple[list[dict], ...]) -> None:
    """Пункт меню: показать все площадки."""
    show_venues(data[1])


def menu_find_venue(data: tuple[list[dict], ...]) -> None:
    """Пункт меню: найти площадку по подстроке названия."""
    query = input("Название площадки: ")
    show_venues(venues.find_venues(data[1], query))


def menu_filter_venues(data: tuple[list[dict], ...]) -> None:
    """Пункт меню: отобрать площадки по минимальной вместимости."""
    min_capacity = input_int("Минимальная вместимость: ")
    show_venues(venues.filter_venues_by_capacity(data[1], min_capacity))


def menu_check_venue(data: tuple[list[dict], ...]) -> None:
    """Пункт меню: проверить доступность площадки на дату."""
    venue_id = input_int("Идентификатор площадки: ")
    check_date = input_date("Дата (ДД.ММ.ГГГГ): ")
    if concerts.is_venue_available(data[3], venue_id, check_date):
        print("Площадка свободна")
    else:
        print("Площадка занята")


def menu_add_concert(data: tuple[list[dict], ...]) -> None:
    """Пункт меню: добавить концерт."""
    title = input("Название концерта: ")
    performer_id = input_int("Идентификатор исполнителя: ")
    venue_id = input_int("Идентификатор площадки: ")
    program_id = input_int("Идентификатор программы: ")
    concert_date = input_date("Дата (ДД.ММ.ГГГГ): ")
    expected_guests = input_int("Ожидаемое число зрителей: ")
    if not concerts.is_venue_available(data[3], venue_id, concert_date):
        print("Ошибка: площадка занята на эту дату")
        return
    venue = venues.get_venue_by_id(data[1], venue_id)
    if venue is None:
        print("Ошибка: площадка не найдена")
        return
    if expected_guests > venue["capacity"]:
        print("Ошибка: площадка не вмещает всех зрителей")
        return
    concerts.add_concert(
        data[3],
        title,
        performer_id,
        venue_id,
        program_id,
        concert_date,
        expected_guests,
        2000.0,
    )
    print("Концерт добавлен")


def menu_cancel_concert(data: tuple[list[dict], ...]) -> None:
    """Пункт меню: отменить концерт."""
    concert_id = input_int("Идентификатор концерта: ")
    if concerts.cancel_concert(data[3], concert_id):
        print("Концерт отменен")
    else:
        print("Ошибка: концерт не найден")


def menu_statistics(data: tuple[list[dict], ...]) -> None:
    """Пункт меню: вывести статистику концертов."""
    statistics = concerts.get_concerts_statistics(data[3], date.today())
    print(f"Запланировано концертов: {statistics['planned']}")
    print(f"Прошедших концертов: {statistics['past']}")
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


def main() -> None:
    """Основной цикл меню приложения."""
    data = load_all_data()
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
        save_all_data(*data)


if __name__ == "__main__":
    main()
