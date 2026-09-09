"""Начальный сценарий системы учета концертных выступлений (ПР1).

Используются конструкции Python из ПР1: простые типы данных, операции,
преобразование типов, условные конструкции, функции, импорт модулей.
"""

from datetime import date

# Исполнитель
artist_name = "Мейби Бейби"
artist_genre = "гиперпоп"
artist_rating = 9.2

# Площадка
venue_name = "Adrenaline Stadium"
venue_capacity = 5000

# Программа
program_name = "MAYDAY: клубный сет"
program_duration = 90
program_age_limit = 16

# Концерт
concert_title = "Клубный вечер с Мейби Бейби"
concert_date = date(2026, 10, 15)
expected_guests = 4800
base_ticket_price = 2500.0

# Зритель
guest_name = "Иван Петров"
guest_age = 25


def get_concert_status(concert_date, today):
    """Определяет статус концерта относительно сегодняшней даты."""
    if concert_date > today:
        return "Запланирован"
    elif concert_date == today:
        return "Идет сегодня"
    return "Завершен"


def check_venue_fit(expected_guests, venue_capacity):
    """Проверяет, вмещает ли площадка ожидаемое число зрителей."""
    if expected_guests > venue_capacity:
        return "Площадка не вмещает всех зрителей"
    free_seats = venue_capacity - expected_guests
    return "Площадка подходит, свободных мест: " + str(free_seats)


def calculate_ticket_price(base_price, rating):
    """Рассчитывает цену билета с учетом рейтинга исполнителя."""
    if rating >= 9.0:
        multiplier = 1.5
    elif rating >= 7.0:
        multiplier = 1.2
    else:
        multiplier = 1.0
    return round(base_price * multiplier, 2)


def is_guest_allowed(guest_age, age_limit):
    """Проверяет допуск зрителя по возрастному ограничению программы."""
    return guest_age >= age_limit


def calculate_revenue(ticket_price, expected_guests):
    """Рассчитывает ожидаемую выручку концерта."""
    return ticket_price * expected_guests


def main():
    today = date.today()

    print("Система учета концертных выступлений")
    print("Концерт: " + concert_title)
    print("Дата: " + str(concert_date))
    print("Исполнитель: " + artist_name + " (" + artist_genre + ")")
    print("Площадка: " + venue_name)
    print(
        "Программа: "
        + program_name
        + ", продолжительность: "
        + str(program_duration)
        + " мин"
    )
    print()

    status = get_concert_status(concert_date, today)
    print("Статус концерта: " + status)

    print(check_venue_fit(expected_guests, venue_capacity))

    ticket_price = calculate_ticket_price(base_ticket_price, artist_rating)
    print("Цена билета: " + str(ticket_price) + " руб.")

    if is_guest_allowed(guest_age, program_age_limit):
        print("Зрителю " + guest_name + " разрешен вход на концерт")
    else:
        print(
            "Зрителю " + guest_name + " вход запрещен: возрастное "
            "ограничение " + str(program_age_limit) + "+"
        )

    revenue = calculate_revenue(ticket_price, expected_guests)
    print("Ожидаемая выручка: " + str(int(revenue)) + " руб.")


if __name__ == "__main__":
    main()
