"""Класс Concert и функции работы с коллекцией концертов."""

from datetime import date

from .performers import Performer, get_performer_by_id
from .programs import Program, get_program_by_id
from .venues import Venue, get_venue_by_id


class Concert:
    """Концертное выступление.

    Связывает объекты Performer, Venue и Program: вместо хранения
    идентификаторов концерт содержит ссылки на связанные объекты.
    """

    def __init__(
        self,
        concert_id: int,
        title: str,
        performer: Performer,
        venue: Venue,
        program: Program,
        concert_date: date,
        expected_guests: int,
        base_ticket_price: float,
    ) -> None:
        """Создать объект концерта."""
        self.id = concert_id
        self.title = title
        self.performer = performer
        self.venue = venue
        self.program = program
        self.date = concert_date
        self.expected_guests = expected_guests
        self.base_ticket_price = base_ticket_price
        self.is_cancelled = False

    @classmethod
    def from_data(
        cls,
        data: dict,
        performers: list[Performer],
        venues: list[Venue],
        programs: list[Program],
    ) -> "Concert | None":
        """Создать концерт из данных JSON, восстановив связи с объектами.

        Если исполнитель, площадка или программа не найдены,
        возвращает None — концерт не создается.
        """
        performer = get_performer_by_id(performers, data["performer_id"])
        venue = get_venue_by_id(venues, data["venue_id"])
        program = get_program_by_id(programs, data["program_id"])
        if performer is None or venue is None or program is None:
            return None
        concert = cls(
            concert_id=data["id"],
            title=data["title"],
            performer=performer,
            venue=venue,
            program=program,
            concert_date=date.fromisoformat(data["date"]),
            expected_guests=data["expected_guests"],
            base_ticket_price=data["base_ticket_price"],
        )
        concert.is_cancelled = data.get("is_cancelled", False)
        return concert

    def to_data(self) -> dict:
        """Преобразовать концерт в данные для JSON.

        Объектные ссылки performer, venue и program преобразуются
        в идентификаторы связанных объектов.
        """
        return {
            "id": self.id,
            "title": self.title,
            "performer_id": self.performer.id,
            "venue_id": self.venue.id,
            "program_id": self.program.id,
            "date": self.date.isoformat(),
            "expected_guests": self.expected_guests,
            "base_ticket_price": self.base_ticket_price,
            "is_cancelled": self.is_cancelled,
        }

    def get_status(self, today: date) -> str:
        """Определить статус концерта относительно сегодняшней даты."""
        if self.is_cancelled:
            return "Отменен"
        if self.date > today:
            return "Запланирован"
        elif self.date == today:
            return "Идет сегодня"
        return "Завершен"

    def calculate_ticket_price(self) -> float:
        """Рассчитать цену билета с учетом рейтинга исполнителя."""
        if self.performer.rating >= 9.0:
            multiplier = 1.5
        elif self.performer.rating >= 7.0:
            multiplier = 1.2
        else:
            multiplier = 1.0
        return round(self.base_ticket_price * multiplier, 2)

    def check_venue_fit(self) -> str:
        """Проверить, вмещает ли площадка ожидаемое число зрителей."""
        if self.venue.is_suitable_for(self.expected_guests):
            free_seats = self.venue.capacity - self.expected_guests
            return "Площадка подходит, свободных мест: " + str(free_seats)
        return "Площадка не вмещает всех зрителей"

    def calculate_revenue(self) -> float:
        """Рассчитать ожидаемую выручку концерта."""
        return self.calculate_ticket_price() * self.expected_guests

    def cancel(self) -> None:
        """Отменить концерт, изменив его состояние."""
        self.is_cancelled = True

    def blocks_venue(self, venue_id: int, check_date: date) -> bool:
        """Проверить, блокирует ли концерт площадку на указанную дату."""
        return (
            not self.is_cancelled
            and self.venue.id == venue_id
            and self.date == check_date
        )

    def __str__(self) -> str:
        """Вернуть строковое представление концерта."""
        status = "отменен" if self.is_cancelled else "активен"
        return (
            f"{self.title} — {self.performer.name}, "
            f"{self.venue.name}, {self.date} ({status})"
        )


def add_concert(
    concerts: list[Concert],
    title: str,
    performer: Performer,
    venue: Venue,
    program: Program,
    concert_date: date,
    expected_guests: int,
    base_ticket_price: float,
) -> Concert:
    """Создать объект концерта и добавить его в коллекцию."""
    concert_id = max((c.id for c in concerts), default=0) + 1
    concert = Concert(
        concert_id=concert_id,
        title=title,
        performer=performer,
        venue=venue,
        program=program,
        concert_date=concert_date,
        expected_guests=expected_guests,
        base_ticket_price=base_ticket_price,
    )
    concerts.append(concert)
    return concert


def cancel_concert(concerts: list[Concert], concert_id: int) -> bool:
    """Найти концерт по идентификатору и отменить его."""
    concert = get_concert_by_id(concerts, concert_id)
    if concert is None:
        return False
    concert.cancel()
    return True


def is_venue_available(
    concerts: list[Concert],
    venue_id: int,
    check_date: date,
) -> bool:
    """Проверить, свободна ли площадка на дату.

    Отмененный концерт площадку не блокирует.
    """
    for concert in concerts:
        if concert.blocks_venue(venue_id, check_date):
            return False
    return True


def find_concerts(concerts: list[Concert], query: str) -> list[Concert]:
    """Найти концерты по подстроке названия (без учета регистра)."""
    query = query.lower()
    return [c for c in concerts if query in c.title.lower()]


def sort_concerts_by_date(concerts: list[Concert]) -> list[Concert]:
    """Вернуть концерты, упорядоченные по дате."""
    return sorted(concerts, key=lambda c: c.date)


def get_upcoming_concerts(
    concerts: list[Concert],
    today: date,
) -> list[Concert]:
    """Отобрать активные концерты, запланированные не раньше today."""
    return [c for c in concerts if not c.is_cancelled and c.date >= today]


def get_concerts_statistics(
    concerts: list[Concert],
    today: date,
) -> dict:
    """Собрать статистику: число запланированных и прошедших концертов."""
    statistics = {
        "planned": 0,
        "past": 0,
        "cancelled": 0,
        "total_guests": 0,
    }
    for concert in concerts:
        if concert.is_cancelled:
            statistics["cancelled"] += 1
        elif concert.date >= today:
            statistics["planned"] += 1
            statistics["total_guests"] += concert.expected_guests
        else:
            statistics["past"] += 1
    return statistics


def get_concert_by_id(
    concerts: list[Concert],
    concert_id: int,
) -> Concert | None:
    """Вернуть концерт по идентификатору или None."""
    for concert in concerts:
        if concert.id == concert_id:
            return concert
    return None
