"""Функции для работы с концертными программами."""


def add_program(
    programs: list[dict],
    name: str,
    duration: int,
    age_limit: int,
) -> None:
    """Добавить программу в список programs."""
    program_id = max((p["id"] for p in programs), default=0) + 1
    programs.append(
        {
            "id": program_id,
            "name": name,
            "duration": duration,
            "age_limit": age_limit,
        }
    )


def find_programs(programs: list[dict], query: str) -> list[dict]:
    """Найти программы по подстроке названия (без учета регистра)."""
    query = query.lower()
    return [p for p in programs if query in p["name"].lower()]


def filter_programs_by_age_limit(
    programs: list[dict],
    max_age_limit: int,
) -> list[dict]:
    """Отобрать программы с ограничением возраста не выше max_age_limit."""
    return [p for p in programs if p["age_limit"] <= max_age_limit]


def sort_programs_by_duration(programs: list[dict]) -> list[dict]:
    """Вернуть программы, упорядоченные по продолжительности."""
    return sorted(programs, key=lambda p: p["duration"])


def get_program_by_id(programs: list[dict], program_id: int) -> dict | None:
    """Вернуть программу по идентификатору или None."""
    for program in programs:
        if program["id"] == program_id:
            return program
    return None
