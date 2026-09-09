"""Тесты функций работы с концертами."""

from datetime import date

from concerts import (
    add_concert,
    calculate_ticket_price,
    cancel_concert,
    get_concert_status,
    is_venue_available,
)


def make_concerts() -> list[dict]:
    """Подготовить тестовый список концертов."""
    concerts = []
    add_concert(
        concerts,
        "Тестовый концерт",
        1,
        1,
        1,
        date(2026, 10, 15),
        100,
        2000.0,
    )
    return concerts


def test_get_concert_status() -> None:
    today = date(2026, 9, 9)
    assert get_concert_status(date(2026, 10, 15), today) == "Запланирован"
    assert get_concert_status(date(2026, 9, 9), today) == "Идет сегодня"
    assert get_concert_status(date(2026, 9, 1), today) == "Завершен"


def test_calculate_ticket_price() -> None:
    assert calculate_ticket_price(2000.0, 9.2) == 3000.0
    assert calculate_ticket_price(2000.0, 8.0) == 2400.0
    assert calculate_ticket_price(2000.0, 6.5) == 2000.0


def test_is_venue_available() -> None:
    concerts = make_concerts()
    assert not is_venue_available(concerts, 1, date(2026, 10, 15))
    assert is_venue_available(concerts, 1, date(2026, 10, 16))


def test_cancel_concert() -> None:
    concerts = make_concerts()
    assert cancel_concert(concerts, 1)
    assert concerts == []
    assert not cancel_concert(concerts, 99)


def test_duplicate_concert_forbidden() -> None:
    concerts = make_concerts()
    assert not is_venue_available(concerts, 1, date(2026, 10, 15))
