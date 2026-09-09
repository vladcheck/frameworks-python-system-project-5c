"""Функции для работы с концертными площадками."""


def add_venue(
    venues: list[dict],
    name: str,
    city: str,
    capacity: int,
) -> None:
    """Добавить площадку в список venues."""
    venue_id = max((v["id"] for v in venues), default=0) + 1
    venues.append(
        {
            "id": venue_id,
            "name": name,
            "city": city,
            "capacity": capacity,
        }
    )


def find_venues(venues: list[dict], query: str) -> list[dict]:
    """Найти площадки по подстроке названия (без учета регистра)."""
    query = query.lower()
    return [v for v in venues if query in v["name"].lower()]


def filter_venues_by_capacity(
    venues: list[dict],
    min_capacity: int,
) -> list[dict]:
    """Отобрать площадки, вмещающие не меньше min_capacity человек."""
    return [v for v in venues if v["capacity"] >= min_capacity]


def sort_venues_by_capacity(venues: list[dict]) -> list[dict]:
    """Вернуть площадки, упорядоченные по вместимости (по возрастанию)."""
    return sorted(venues, key=lambda v: v["capacity"])


def get_venue_by_id(venues: list[dict], venue_id: int) -> dict | None:
    """Вернуть площадку по идентификатору или None."""
    for venue in venues:
        if venue["id"] == venue_id:
            return venue
    return None
