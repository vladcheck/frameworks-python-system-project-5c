"""Функции для работы с исполнителями."""


def add_performer(
    performers: list[dict],
    name: str,
    genre: str,
    rating: float,
) -> None:
    """Добавить исполнителя в список performers."""
    performer_id = max((p["id"] for p in performers), default=0) + 1
    performers.append(
        {
            "id": performer_id,
            "name": name,
            "genre": genre,
            "rating": rating,
        }
    )


def find_performers(performers: list[dict], query: str) -> list[dict]:
    """Найти исполнителей по подстроке имени (без учета регистра)."""
    query = query.lower()
    return [p for p in performers if query in p["name"].lower()]


def sort_performers_by_rating(performers: list[dict]) -> list[dict]:
    """Вернуть исполнителей, упорядоченных по рейтингу (по убыванию)."""
    return sorted(performers, key=lambda p: p["rating"], reverse=True)


def get_performer_by_id(
    performers: list[dict],
    performer_id: int,
) -> dict | None:
    """Вернуть исполнителя по id или None."""
    for performer in performers:
        if performer["id"] == performer_id:
            return performer
    return None
