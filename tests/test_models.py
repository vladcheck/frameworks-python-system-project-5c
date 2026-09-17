"""Тесты классов Performer и Program."""

from src.models import Performer, Program


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


def test_program_from_data() -> None:
    data = {"id": 1, "name": "MAYDAY", "duration": 90, "age_limit": 16}
    program = Program.from_data(data)
    assert program.id == 1
    assert program.to_data() == data
