"""Тесты класса Concert и функций работы с концертами."""

from datetime import date

from src.models import Concert, Performer, Program, Venue
from src.models.concerts import (
    add_concert,
    cancel_concert,
    get_concert_by_id,
    is_venue_available,
)


def make_concert() -> Concert:
    """Создать тестовый концерт со связанными объектами."""
    performer = Performer(1, "Мейби Бейби", "гиперпоп", 9.2)
    venue = Venue(1, "Adrenaline Stadium", "Москва", 5000)
    program = Program(1, "MAYDAY", 90, 16)
    return Concert(
        concert_id=1,
        title="Клубный вечер",
        performer=performer,
        venue=venue,
        program=program,
        concert_date=date(2026, 10, 15),
        expected_guests=4800,
        base_ticket_price=2500.0,
    )


def make_concerts() -> list[Concert]:
    """Подготовить тестовую коллекцию концертов."""
    concert = make_concert()
    return [concert]


def test_concert_creation() -> None:
    concert = make_concert()
    assert concert.id == 1
    assert concert.title == "Клубный вечер"
    assert concert.performer.name == "Мейби Бейби"
    assert concert.venue.name == "Adrenaline Stadium"
    assert concert.program.name == "MAYDAY"
    assert concert.date == date(2026, 10, 15)
    assert concert.expected_guests == 4800
    assert not concert.is_cancelled


def test_concert_get_status() -> None:
    concert = make_concert()
    today = date(2026, 9, 9)
    assert concert.get_status(today) == "Запланирован"
    assert concert.get_status(date(2026, 10, 15)) == "Идет сегодня"
    assert concert.get_status(date(2026, 11, 1)) == "Завершен"


def test_concert_calculate_ticket_price() -> None:
    concert = make_concert()
    assert concert.calculate_ticket_price() == 3750.0


def test_concert_check_venue_fit() -> None:
    concert = make_concert()
    assert "свободных мест: 200" in concert.check_venue_fit()


def test_concert_cancel() -> None:
    concert = make_concert()
    concert.cancel()
    assert concert.is_cancelled
    assert concert.get_status(date(2026, 9, 9)) == "Отменен"


def test_concert_to_data() -> None:
    concert = make_concert()
    data = concert.to_data()
    assert data["id"] == 1
    assert data["performer_id"] == 1
    assert data["venue_id"] == 1
    assert data["program_id"] == 1
    assert data["date"] == "2026-10-15"
    assert data["is_cancelled"] is False


def test_concert_from_data() -> None:
    performers = [Performer(1, "Мейби Бейби", "гиперпоп", 9.2)]
    venues = [Venue(1, "Adrenaline Stadium", "Москва", 5000)]
    programs = [Program(1, "MAYDAY", 90, 16)]
    data = {
        "id": 1,
        "title": "Клубный вечер",
        "performer_id": 1,
        "venue_id": 1,
        "program_id": 1,
        "date": "2026-10-15",
        "expected_guests": 4800,
        "base_ticket_price": 2500.0,
        "is_cancelled": False,
    }
    concert = Concert.from_data(data, performers, venues, programs)
    assert concert is not None
    assert concert.performer is performers[0]
    assert concert.venue is venues[0]
    assert concert.program is programs[0]


def test_concert_from_data_missing_links() -> None:
    concert = Concert.from_data(
        {"performer_id": 99, "venue_id": 99, "program_id": 99},
        [],
        [],
        [],
    )
    assert concert is None


def test_is_venue_available() -> None:
    concerts = make_concerts()
    assert not is_venue_available(concerts, 1, date(2026, 10, 15))
    assert is_venue_available(concerts, 1, date(2026, 10, 16))


def test_cancelled_concert_does_not_block_venue() -> None:
    concerts = make_concerts()
    concerts[0].cancel()
    assert is_venue_available(concerts, 1, date(2026, 10, 15))


def test_add_and_cancel_concert() -> None:
    concerts = []
    performer = Performer(1, "Мейби Бейби", "гиперпоп", 9.2)
    venue = Venue(1, "Adrenaline Stadium", "Москва", 5000)
    program = Program(1, "MAYDAY", 90, 16)
    concert = add_concert(
        concerts,
        "Тест",
        performer,
        venue,
        program,
        date(2026, 10, 15),
        100,
        2000.0,
    )
    assert get_concert_by_id(concerts, concert.id) is concert
    assert cancel_concert(concerts, concert.id)
    assert concert.is_cancelled
    assert len(concerts) == 1
    assert not cancel_concert(concerts, 99)
