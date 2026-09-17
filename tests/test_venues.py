"""Тесты класса Venue и функций работы с площадками."""

from models import Venue
from models.venues import (
    add_venue,
    filter_venues_by_capacity,
    find_venues,
    get_venue_by_id,
    sort_venues_by_capacity,
)


def make_venues() -> list[Venue]:
    """Подготовить тестовую коллекцию площадок."""
    venues = []
    add_venue(venues, "Космонавт", "Санкт-Петербург", 1500)
    add_venue(venues, "Adrenaline Stadium", "Москва", 5000)
    return venues


def test_venue_creation() -> None:
    venue = Venue(1, "Космонавт", "Санкт-Петербург", 1500)
    assert venue.id == 1
    assert venue.name == "Космонавт"
    assert venue.city == "Санкт-Петербург"
    assert venue.capacity == 1500
    assert str(venue)


def test_venue_is_suitable_for() -> None:
    venue = Venue(1, "Космонавт", "Санкт-Петербург", 1500)
    assert venue.is_suitable_for(1500)
    assert not venue.is_suitable_for(1501)


def test_venue_validate_capacity() -> None:
    assert Venue.validate_capacity(100)
    assert not Venue.validate_capacity(0)


def test_venue_from_data() -> None:
    data = {"id": 1, "name": "Космонавт", "city": "Санкт-Петербург", "capacity": 1500}
    venue = Venue.from_data(data)
    assert venue.id == 1
    assert venue.to_data() == data


def test_add_venue() -> None:
    venues = make_venues()
    assert len(venues) == 2
    assert venues[0].id == 1
    assert venues[1].id == 2


def test_find_venues() -> None:
    venues = make_venues()
    found = find_venues(venues, "космо")
    assert len(found) == 1
    assert found[0].name == "Космонавт"


def test_filter_venues_by_capacity() -> None:
    venues = make_venues()
    filtered = filter_venues_by_capacity(venues, 2000)
    assert len(filtered) == 1
    assert filtered[0].name == "Adrenaline Stadium"


def test_sort_venues_by_capacity() -> None:
    venues = make_venues()
    sorted_venues = sort_venues_by_capacity(venues)
    assert sorted_venues[0].capacity == 1500


def test_get_venue_by_id() -> None:
    venues = make_venues()
    venue = get_venue_by_id(venues, 1)
    assert venue is not None
    assert venue.name == "Космонавт"
    assert get_venue_by_id(venues, 99) is None
