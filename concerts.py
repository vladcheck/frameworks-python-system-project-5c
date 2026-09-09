"""Функции для работы с концертами.

Функции get_concert_status, check_venue_fit, calculate_ticket_price,
is_guest_allowed и calculate_revenue перенесены из начального сценария ПР1.
"""

from datetime import date


def get_concert_status(concert_date: date, today: date) -> str:
    """Определить статус концерта относительно сегодняшней даты."""
    if concert_date > today:
        return "Запланирован"
    elif concert_date == today:
        return "Идет сегодня"
    return "Завершен"


def check_venue_fit(expected_guests: int, venue_capacity: int) -> str:
    """Проверить, вмещает ли площадка ожидаемое число зрителей."""
    if expected_guests > venue_capacity:
        return "Площадка не вмещает всех зрителей"
    free_seats = venue_capacity - expected_guests
    return "Площадка подходит, свободных мест: " + str(free_seats)


def calculate_ticket_price(base_price: float, rating: float) -> float:
    """Рассчитать цену билета с учетом рейтинга исполнителя."""
    if rating >= 9.0:
        multiplier = 1.5
    elif rating >= 7.0:
        multiplier = 1.2
    else:
        multiplier = 1.0
    return round(base_price * multiplier, 2)


def is_guest_allowed(guest_age: int, age_limit: int) -> bool:
    """Проверить допуск зрителя по возрастному ограничению программы."""
    return guest_age >= age_limit


def calculate_revenue(ticket_price: float, expected_guests: int) -> float:
    """Рассчитать ожидаемую выручку концерта."""
    return ticket_price * expected_guests


def add_concert(
    concerts: list[dict],
    title: str,
    performer_id: int,
    venue_id: int,
    program_id: int,
    concert_date: date,
    expected_guests: int,
    base_ticket_price: float,
) -> None:
    """Добавить концерт в список concerts."""
    concert_id = max((c["id"] for c in concerts), default=0) + 1
    concerts.append(
        {
            "id": concert_id,
            "title": title,
            "performer_id": performer_id,
            "venue_id": venue_id,
            "program_id": program_id,
            "date": concert_date.isoformat(),
            "expected_guests": expected_guests,
            "base_ticket_price": base_ticket_price,
        }
    )


def cancel_concert(concerts: list[dict], concert_id: int) -> bool:
    """Отменить концерт: удалить его из списка concerts."""
    for concert in concerts:
        if concert["id"] == concert_id:
            concerts.remove(concert)
            return True
    return False


def is_venue_available(
    concerts: list[dict],
    venue_id: int,
    concert_date: date,
) -> bool:
    """Проверить, свободна ли площадка на дату."""
    for concert in concerts:
        if (
            concert["venue_id"] == venue_id
            and concert["date"] == concert_date.isoformat()
        ):
            return False
    return True


def find_concerts(concerts: list[dict], query: str) -> list[dict]:
    """Найти концерты по подстроке названия (без учета регистра)."""
    query = query.lower()
    return [c for c in concerts if query in c["title"].lower()]


def sort_concerts_by_date(concerts: list[dict]) -> list[dict]:
    """Вернуть концерты, упорядоченные по дате (от ранних к поздним)."""
    return sorted(concerts, key=lambda c: c["date"])


def get_upcoming_concerts(
    concerts: list[dict],
    today: date,
) -> list[dict]:
    """Отобрать концерты, запланированные на дату не раньше today."""
    return [c for c in concerts if c["date"] >= today.isoformat()]


def get_concerts_statistics(concerts: list[dict], today: date) -> dict:
    """Собрать статистику: число запланированных и прошедших концертов."""
    statistics = {"planned": 0, "past": 0, "total_guests": 0}
    for concert in concerts:
        if concert["date"] >= today.isoformat():
            statistics["planned"] += 1
            statistics["total_guests"] += concert["expected_guests"]
        else:
            statistics["past"] += 1
    return statistics
