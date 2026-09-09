"""Тесты функций работы с площадками."""

from venues import (
    add_venue,
    filter_venues_by_capacity,
    find_venues,
    get_venue_by_id,
    sort_venues_by_capacity,
)


def make_venues() -> list[dict]:
    """Подготовить тестовый список площадок."""
    venues = []
    add_venue(venues, "Космонавт", "Санкт-Петербург", 1500)
    add_venue(venues, "Adrenaline Stadium", "Москва", 5000)
    return venues


def test_add_venue() -> None:
    venues = make_venues()
    assert len(venues) == 2
    assert venues[0]["id"] == 1
    assert venues[1]["id"] == 2


def test_find_venues() -> None:
    venues = make_venues()
    found = find_venues(venues, "космо")
    assert len(found) == 1
    assert found[0]["name"] == "Космонавт"


def test_filter_venues_by_capacity() -> None:
    venues = make_venues()
    filtered = filter_venues_by_capacity(venues, 2000)
    assert len(filtered) == 1
    assert filtered[0]["name"] == "Adrenaline Stadium"


def test_sort_venues_by_capacity() -> None:
    venues = make_venues()
    sorted_venues = sort_venues_by_capacity(venues)
    assert sorted_venues[0]["capacity"] == 1500


def test_get_venue_by_id() -> None:
    venues = make_venues()
    assert get_venue_by_id(venues, 1)["name"] == "Космонавт"
    assert get_venue_by_id(venues, 99) is None
