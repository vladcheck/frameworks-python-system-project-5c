"""Класс Performer и функции работы с коллекцией исполнителей."""


class Performer:
    """Исполнитель концертных выступлений."""

    def __init__(
        self,
        performer_id: int,
        name: str,
        genre: str,
        rating: float,
    ) -> None:
        """Создать объект исполнителя."""
        self.id = performer_id
        self.name = name
        self.genre = genre
        self.rating = rating

    @classmethod
    def from_data(cls, data: dict) -> "Performer":
        """Создать исполнителя из набора данных JSON."""
        return cls(
            performer_id=data["id"],
            name=data["name"],
            genre=data["genre"],
            rating=data["rating"],
        )

    def to_data(self) -> dict:
        """Преобразовать исполнителя в данные для JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "genre": self.genre,
            "rating": self.rating,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление исполнителя."""
        return f"{self.name} ({self.genre}), рейтинг {self.rating}"


def add_performer(
    performers: list[Performer],
    name: str,
    genre: str,
    rating: float,
) -> Performer:
    """Создать объект исполнителя и добавить его в коллекцию."""
    performer_id = max((p.id for p in performers), default=0) + 1
    performer = Performer(performer_id, name, genre, rating)
    performers.append(performer)
    return performer


def find_performers(
    performers: list[Performer],
    query: str,
) -> list[Performer]:
    """Найти исполнителей по подстроке имени (без учета регистра)."""
    query = query.lower()
    return [p for p in performers if query in p.name.lower()]


def sort_performers_by_rating(
    performers: list[Performer],
) -> list[Performer]:
    """Вернуть исполнителей, упорядоченных по рейтингу (по убыванию)."""
    return sorted(performers, key=lambda p: p.rating, reverse=True)


def get_performer_by_id(
    performers: list[Performer],
    performer_id: int,
) -> Performer | None:
    """Вернуть исполнителя по идентификатору или None."""
    for performer in performers:
        if performer.id == performer_id:
            return performer
    return None
