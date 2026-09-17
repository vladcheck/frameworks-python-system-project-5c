"""Тесты класса Concert и функций работы с концертами."""

from datetime import date

from src.models import Concert, Performer, Program, Venue
from src.models.concerts import (
    add_concert,
    cancel_concert,
    find_concerts,
    get_concert_by_id,
    get_concerts_statistics,
    get_upcoming_concerts,
    is_venue_available,
    sort_concerts_by_date,
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


def test_concert_get_status_cancelled_overrides_date() -> None:
    concert = make_concert()
    concert.cancel()
    assert concert.get_status(date(2026, 11, 1)) == "Отменен"


def test_concert_calculate_ticket_price() -> None:
    concert = make_concert()
    assert concert.calculate_ticket_price() == 3750.0


def test_concert_calculate_ticket_price_multiplier_boundaries() -> None:
    venue = Venue(1, "Зал", "Москва", 100)
    program = Program(1, "Шоу", 60, 0)
    for rating, multiplier in [(9.0, 1.5), (8.99, 1.2), (7.0, 1.2), (6.9, 1.0)]:
        performer = Performer(1, "Артист", "поп", rating)
        concert = Concert(
            1, "Шоу", performer, venue, program, date(2026, 1, 1), 1, 1000.0
        )
        assert concert.calculate_ticket_price() == round(1000.0 * multiplier, 2)


def test_concert_calculate_ticket_price_rounding() -> None:
    performer = Performer(1, "Артист", "поп", 7.0)
    venue = Venue(1, "Зал", "Москва", 100)
    program = Program(1, "Шоу", 60, 0)
    concert = Concert(1, "Шоу", performer, venue, program, date(2026, 1, 1), 1, 999.99)
    assert concert.calculate_ticket_price() == 1199.99


def test_concert_check_venue_fit() -> None:
    concert = make_concert()
    assert "свободных мест: 200" in concert.check_venue_fit()


def test_concert_check_venue_fit_not_suitable() -> None:
    concert = make_concert()
    concert.expected_guests = 5001
    assert concert.check_venue_fit() == "Площадка не вмещает всех зрителей"


def test_concert_calculate_revenue() -> None:
    concert = make_concert()
    assert concert.calculate_revenue() == 3750.0 * 4800


def test_concert_blocks_venue() -> None:
    concert = make_concert()
    assert concert.blocks_venue(1, date(2026, 10, 15))
    assert not concert.blocks_venue(2, date(2026, 10, 15))
    assert not concert.blocks_venue(1, date(2026, 10, 16))


def test_concert_blocks_venue_when_cancelled() -> None:
    concert = make_concert()
    concert.cancel()
    assert not concert.blocks_venue(1, date(2026, 10, 15))


def test_concert_str() -> None:
    concert = make_concert()
    text = str(concert)
    assert "Клубный вечер" in text
    assert "активен" in text
    concert.cancel()
    assert "отменен" in str(concert)


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


def test_concert_from_data_missing_cancelled_flag() -> None:
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
    }
    concert = Concert.from_data(data, performers, venues, programs)
    assert concert is not None
    assert concert.is_cancelled is False


def test_concert_from_data_restores_cancelled_state() -> None:
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
        "is_cancelled": True,
    }
    concert = Concert.from_data(data, performers, venues, programs)
    assert concert is not None
    assert concert.is_cancelled is True


def test_concert_from_data_missing_links() -> None:
    concert = Concert.from_data(
        {"performer_id": 99, "venue_id": 99, "program_id": 99},
        [],
        [],
        [],
    )
    assert concert is None


def test_concert_from_data_partially_missing_links() -> None:
    performers = [Performer(1, "Мейби Бейби", "гиперпоп", 9.2)]
    concert = Concert.from_data(
        {"performer_id": 1, "venue_id": 99, "program_id": 99},
        performers,
        [],
        [],
    )
    assert concert is None


def test_is_venue_available() -> None:
    concerts = make_concerts()
    assert not is_venue_available(concerts, 1, date(2026, 10, 15))
    assert is_venue_available(concerts, 1, date(2026, 10, 16))


def test_is_venue_available_empty_collection() -> None:
    assert is_venue_available([], 1, date(2026, 10, 15))


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


def test_add_concert_continues_max_id() -> None:
    concerts = make_concerts()
    performer = Performer(1, "Мейби Бейби", "гиперпоп", 9.2)
    venue = Venue(1, "Adrenaline Stadium", "Москва", 5000)
    program = Program(1, "MAYDAY", 90, 16)
    concert = add_concert(
        concerts, "Еще один", performer, venue, program, date(2026, 10, 16), 100, 2000.0
    )
    assert concert.id == 2


def test_find_concerts() -> None:
    concerts = make_concerts()
    found = find_concerts(concerts, "клубн")
    assert len(found) == 1
    assert found[0].title == "Клубный вечер"


def test_find_concerts_no_match() -> None:
    concerts = make_concerts()
    assert find_concerts(concerts, "симфонический") == []


def test_find_concerts_empty_query_returns_all() -> None:
    concerts = make_concerts()
    assert len(find_concerts(concerts, "")) == 1


def test_sort_concerts_by_date() -> None:
    concert_later = make_concert()
    concert_earlier = make_concert()
    concert_earlier.id = 2
    concert_earlier.date = date(2026, 10, 1)
    sorted_concerts = sort_concerts_by_date([concert_later, concert_earlier])
    assert sorted_concerts[0].date == date(2026, 10, 1)


def test_sort_concerts_by_date_empty() -> None:
    assert sort_concerts_by_date([]) == []


def test_get_upcoming_concerts() -> None:
    upcoming = make_concert()
    today = date(2026, 9, 9)
    past_concert = make_concert()
    past_concert.id = 2
    past_concert.date = date(2026, 9, 1)
    cancelled_concert = make_concert()
    cancelled_concert.id = 3
    cancelled_concert.date = date(2026, 10, 20)
    cancelled_concert.cancel()
    concerts = [upcoming, past_concert, cancelled_concert]
    result = get_upcoming_concerts(concerts, today)
    assert len(result) == 1
    assert result[0] is upcoming


def test_get_upcoming_concerts_includes_today() -> None:
    concert = make_concert()
    today = date(2026, 10, 15)
    result = get_upcoming_concerts([concert], today)
    assert len(result) == 1


def test_get_upcoming_concerts_empty() -> None:
    assert get_upcoming_concerts([], date(2026, 9, 9)) == []


def test_get_concerts_statistics() -> None:
    today = date(2026, 9, 9)
    planned = make_concert()
    planned.id = 1
    planned.expected_guests = 100
    past_concert = make_concert()
    past_concert.id = 2
    past_concert.date = date(2026, 9, 1)
    cancelled_concert = make_concert()
    cancelled_concert.id = 3
    cancelled_concert.cancel()
    statistics = get_concerts_statistics(
        [planned, past_concert, cancelled_concert], today
    )
    assert statistics == {
        "planned": 1,
        "past": 1,
        "cancelled": 1,
        "total_guests": 100,
    }


def test_get_concerts_statistics_empty() -> None:
    statistics = get_concerts_statistics([], date(2026, 9, 9))
    assert statistics == {"planned": 0, "past": 0, "cancelled": 0, "total_guests": 0}
