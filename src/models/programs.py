"""Класс Program и функции работы с коллекцией программ."""


class Program:
    """Концертная программа."""

    def __init__(
        self,
        program_id: int,
        name: str,
        duration: int,
        age_limit: int,
    ) -> None:
        """Создать объект программы."""
        self.id = program_id
        self.name = name
        self.duration = duration
        self.age_limit = age_limit

    @classmethod
    def from_data(cls, data: dict) -> "Program":
        """Создать программу из набора данных JSON."""
        return cls(
            program_id=data["id"],
            name=data["name"],
            duration=data["duration"],
            age_limit=data["age_limit"],
        )

    def to_data(self) -> dict:
        """Преобразовать программу в данные для JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "duration": self.duration,
            "age_limit": self.age_limit,
        }

    def is_allowed_for(self, guest_age: int) -> bool:
        """Проверить допуск зрителя по возрастному ограничению."""
        return guest_age >= self.age_limit

    def __str__(self) -> str:
        """Вернуть строковое представление программы."""
        return (
            f"{self.name}, {self.duration} мин, "
            f"возрастное ограничение {self.age_limit}+"
        )


def add_program(
    programs: list[Program],
    name: str,
    duration: int,
    age_limit: int,
) -> Program:
    """Создать объект программы и добавить его в коллекцию."""
    program_id = max((p.id for p in programs), default=0) + 1
    program = Program(program_id, name, duration, age_limit)
    programs.append(program)
    return program


def find_programs(programs: list[Program], query: str) -> list[Program]:
    """Найти программы по подстроке названия (без учета регистра)."""
    query = query.lower()
    return [p for p in programs if query in p.name.lower()]


def filter_programs_by_age_limit(
    programs: list[Program],
    max_age_limit: int,
) -> list[Program]:
    """Отобрать программы с ограничением возраста не выше max_age_limit."""
    return [p for p in programs if p.age_limit <= max_age_limit]


def sort_programs_by_duration(programs: list[Program]) -> list[Program]:
    """Вернуть программы, упорядоченные по продолжительности."""
    return sorted(programs, key=lambda p: p.duration)


def get_program_by_id(
    programs: list[Program],
    program_id: int,
) -> Program | None:
    """Вернуть программу по идентификатору или None."""
    for program in programs:
        if program.id == program_id:
            return program
    return None
