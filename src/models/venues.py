"""Класс Venue и функции работы с коллекцией площадок."""


class Venue:
    """Концертная площадка."""

    def __init__(
        self,
        venue_id: int,
        name: str,
        city: str,
        capacity: int,
    ) -> None:
        """Создать объект площадки."""
        self.id = venue_id
        self.name = name
        self.city = city
        self.capacity = capacity

    @classmethod
    def from_data(cls, data: dict) -> "Venue":
        """Создать площадку из набора данных JSON."""
        return cls(
            venue_id=data["id"],
            name=data["name"],
            city=data["city"],
            capacity=data["capacity"],
        )

    def to_data(self) -> dict:
        """Преобразовать площадку в данные для JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "capacity": self.capacity,
        }

    def is_suitable_for(self, people_count: int) -> bool:
        """Проверить, вмещает ли площадка указанное число зрителей."""
        return self.capacity >= people_count

    @staticmethod
    def validate_capacity(capacity: int) -> bool:
        """Проверить корректность значения вместимости."""
        return capacity > 0

    def __str__(self) -> str:
        """Вернуть строковое представление площадки."""
        return f"{self.name}, {self.city} ({self.capacity} мест)"


def add_venue(
    venues: list[Venue],
    name: str,
    city: str,
    capacity: int,
) -> Venue:
    """Создать объект площадки и добавить его в коллекцию."""
    venue_id = max((v.id for v in venues), default=0) + 1
    venue = Venue(venue_id, name, city, capacity)
    venues.append(venue)
    return venue


def find_venues(venues: list[Venue], query: str) -> list[Venue]:
    """Найти площадки по подстроке названия (без учета регистра)."""
    query = query.lower()
    return [v for v in venues if query in v.name.lower()]


def filter_venues_by_capacity(
    venues: list[Venue],
    min_capacity: int,
) -> list[Venue]:
    """Отобрать площадки, вмещающие не меньше min_capacity человек."""
    return [v for v in venues if v.is_suitable_for(min_capacity)]


def sort_venues_by_capacity(venues: list[Venue]) -> list[Venue]:
    """Вернуть площадки, упорядоченные по вместимости."""
    return sorted(venues, key=lambda v: v.capacity)


def get_venue_by_id(
    venues: list[Venue],
    venue_id: int,
) -> Venue | None:
    """Вернуть площадку по идентификатору или None."""
    for venue in venues:
        if venue.id == venue_id:
            return venue
    return None
