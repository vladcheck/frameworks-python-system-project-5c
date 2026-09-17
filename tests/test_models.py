"""Тесты классов Performer и Program и функций работы с коллекциями."""

import pytest

from src.models import Performer, Program
from src.models.performers import (
    add_performer,
    find_performers,
    get_performer_by_id,
    sort_performers_by_rating,
)
from src.models.programs import (
    add_program,
    filter_programs_by_age_limit,
    find_programs,
    get_program_by_id,
    sort_programs_by_duration,
)


def make_performers() -> list[Performer]:
    """Подготовить тестовую коллекцию исполнителей."""
    performers = []
    add_performer(performers, "Мейби Бейби", "гиперпоп", 9.2)
    add_performer(performers, "Пошлая Молли", "поп-панк", 8.5)
    return performers


def make_programs() -> list[Program]:
    """Подготовить тестовую коллекцию программ."""
    programs = []
    add_program(programs, "MAYDAY", 90, 16)
    add_program(programs, "Семейное шоу", 60, 0)
    return programs


def test_performer_creation() -> None:
    performer = Performer(1, "Мейби Бейби", "гиперпоп", 9.2)
    assert performer.id == 1
    assert performer.name == "Мейби Бейби"
    assert performer.genre == "гиперпоп"
    assert performer.rating == 9.2
    assert "Мейби Бейби" in str(performer)


def test_performer_from_data() -> None:
    data = {"id": 1, "name": "Мейби Бейби", "genre": "гиперпоп", "rating": 9.2}
    performer = Performer.from_data(data)
    assert performer.id == 1
    assert performer.to_data() == data


def test_performer_from_data_missing_key() -> None:
    with pytest.raises(KeyError):
        Performer.from_data({"id": 1, "name": "Мейби Бейби"})


def test_add_performer_empty_collection() -> None:
    performers = []
    performer = add_performer(performers, "Мейби Бейби", "гиперпоп", 9.2)
    assert performer.id == 1
    assert len(performers) == 1


def test_add_performer_continues_max_id() -> None:
    performers = [Performer(5, "А", "поп", 7.0)]
    performer = add_performer(performers, "Б", "рок", 6.5)
    assert performer.id == 6


def test_find_performers() -> None:
    performers = make_performers()
    found = find_performers(performers, "мейби")
    assert len(found) == 1
    assert found[0].name == "Мейби Бейби"


def test_find_performers_no_match() -> None:
    performers = make_performers()
    assert find_performers(performers, "звезда") == []


def test_find_performers_empty_query_returns_all() -> None:
    performers = make_performers()
    assert len(find_performers(performers, "")) == 2


def test_sort_performers_by_rating() -> None:
    performers = make_performers()
    sorted_performers = sort_performers_by_rating(performers)
    assert sorted_performers[0].rating == 9.2
    assert sorted_performers[1].rating == 8.5


def test_sort_performers_by_rating_empty() -> None:
    assert sort_performers_by_rating([]) == []


def test_get_performer_by_id() -> None:
    performers = make_performers()
    performer = get_performer_by_id(performers, 1)
    assert performer is not None
    assert performer.name == "Мейби Бейби"
    assert get_performer_by_id(performers, 99) is None


def test_program_creation() -> None:
    program = Program(1, "MAYDAY", 90, 16)
    assert program.id == 1
    assert program.name == "MAYDAY"
    assert program.duration == 90
    assert program.age_limit == 16
    assert str(program)


def test_program_is_allowed_for() -> None:
    program = Program(1, "MAYDAY", 90, 16)
    assert program.is_allowed_for(16)
    assert program.is_allowed_for(25)
    assert not program.is_allowed_for(15)


def test_program_is_allowed_for_no_limit() -> None:
    program = Program(1, "Семейное шоу", 60, 0)
    assert program.is_allowed_for(0)


def test_program_from_data() -> None:
    data = {"id": 1, "name": "MAYDAY", "duration": 90, "age_limit": 16}
    program = Program.from_data(data)
    assert program.id == 1
    assert program.to_data() == data


def test_program_from_data_missing_key() -> None:
    with pytest.raises(KeyError):
        Program.from_data({"id": 1, "name": "MAYDAY"})


def test_add_program() -> None:
    programs = make_programs()
    assert len(programs) == 2
    assert programs[0].id == 1
    assert programs[1].id == 2


def test_find_programs() -> None:
    programs = make_programs()
    found = find_programs(programs, "семейн")
    assert len(found) == 1
    assert found[0].name == "Семейное шоу"


def test_find_programs_no_match() -> None:
    programs = make_programs()
    assert find_programs(programs, "новогодняя") == []


def test_filter_programs_by_age_limit() -> None:
    programs = make_programs()
    filtered = filter_programs_by_age_limit(programs, 12)
    assert len(filtered) == 1
    assert filtered[0].age_limit == 0


def test_filter_programs_by_age_limit_exact_match() -> None:
    programs = make_programs()
    filtered = filter_programs_by_age_limit(programs, 16)
    assert len(filtered) == 2


def test_filter_programs_by_age_limit_empty() -> None:
    assert filter_programs_by_age_limit([], 18) == []


def test_sort_programs_by_duration() -> None:
    programs = make_programs()
    sorted_programs = sort_programs_by_duration(programs)
    assert sorted_programs[0].duration == 60


def test_get_program_by_id() -> None:
    programs = make_programs()
    program = get_program_by_id(programs, 2)
    assert program is not None
    assert program.name == "Семейное шоу"
    assert get_program_by_id(programs, 99) is None
