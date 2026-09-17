"""Тесты модуля storage: загрузка и сохранение данных в JSON."""

import json
from datetime import date
from pathlib import Path

import pytest

from src.models import Concert, Performer, Program, Venue
from src import storage


def make_objects() -> tuple[list[Performer], list[Venue], list[Program]]:
    """Подготовить связанные тестовые коллекции объектов."""
    performers = [Performer(1, "Мейби Бейби", "гиперпоп", 9.2)]
    venues = [Venue(1, "Adrenaline Stadium", "Москва", 5000)]
    programs = [Program(1, "MAYDAY", 90, 16)]
    return performers, venues, programs


def make_concert(
    performers: list[Performer],
    venues: list[Venue],
    programs: list[Program],
) -> Concert:
    """Создать тестовый концерт из готовых коллекций."""
    return Concert(
        concert_id=1,
        title="Клубный вечер",
        performer=performers[0],
        venue=venues[0],
        program=programs[0],
        concert_date=date(2026, 10, 15),
        expected_guests=4800,
        base_ticket_price=2500.0,
    )


def test_load_performers_missing_file(tmp_path: Path) -> None:
    assert storage.load_performers(str(tmp_path / "absent.json")) == []


def test_load_performers_invalid_json(tmp_path: Path) -> None:
    bad_file = tmp_path / "broken.json"
    bad_file.write_text("not json", encoding="utf-8")
    assert storage.load_performers(str(bad_file)) == []


def test_performers_round_trip(tmp_path: Path) -> None:
    filename = str(tmp_path / "performers.json")
    performers = [Performer(1, "Мейби Бейби", "гиперпоп", 9.2)]
    storage.save_performers(filename, performers)
    loaded = storage.load_performers(filename)
    assert [p.to_data() for p in loaded] == [p.to_data() for p in performers]


def test_load_performers_missing_key_raises(tmp_path: Path) -> None:
    bad_file = tmp_path / "performers.json"
    bad_file.write_text(json.dumps([{"id": 1}]), encoding="utf-8")
    with pytest.raises(KeyError):
        storage.load_performers(str(bad_file))


def test_venues_round_trip(tmp_path: Path) -> None:
    filename = str(tmp_path / "venues.json")
    venues = [Venue(1, "Космонавт", "Санкт-Петербург", 1500)]
    storage.save_venues(filename, venues)
    loaded = storage.load_venues(filename)
    assert [v.to_data() for v in loaded] == [v.to_data() for v in venues]


def test_load_venues_missing_file(tmp_path: Path) -> None:
    assert storage.load_venues(str(tmp_path / "absent.json")) == []


def test_programs_round_trip(tmp_path: Path) -> None:
    filename = str(tmp_path / "programs.json")
    programs = [Program(1, "MAYDAY", 90, 16)]
    storage.save_programs(filename, programs)
    loaded = storage.load_programs(filename)
    assert [p.to_data() for p in loaded] == [p.to_data() for p in programs]


def test_load_programs_missing_file(tmp_path: Path) -> None:
    assert storage.load_programs(str(tmp_path / "absent.json")) == []


def test_concerts_round_trip(tmp_path: Path) -> None:
    filename = str(tmp_path / "concerts.json")
    performers, venues, programs = make_objects()
    concert = make_concert(performers, venues, programs)
    concert.cancel()
    storage.save_concerts(filename, [concert])
    loaded = storage.load_concerts(filename, performers, venues, programs)
    assert len(loaded) == 1
    assert loaded[0].to_data() == concert.to_data()
    assert loaded[0].performer is performers[0]
    assert loaded[0].venue is venues[0]
    assert loaded[0].program is programs[0]


def test_load_concerts_missing_file(tmp_path: Path) -> None:
    performers, venues, programs = make_objects()
    filename = str(tmp_path / "absent.json")
    assert storage.load_concerts(filename, performers, venues, programs) == []


def test_load_concerts_skips_broken_links(tmp_path: Path) -> None:
    filename = str(tmp_path / "concerts.json")
    performers, venues, programs = make_objects()
    concert = make_concert(performers, venues, programs)
    broken = concert.to_data()
    broken["venue_id"] = 99
    storage.save_concerts(filename, [concert])
    with open(filename, "w", encoding="utf-8") as file:
        json.dump([concert.to_data(), broken], file, ensure_ascii=False)
    loaded = storage.load_concerts(filename, performers, venues, programs)
    assert len(loaded) == 1


def test_save_creates_parent_directories(tmp_path: Path) -> None:
    filename = str(tmp_path / "nested" / "deep" / "performers.json")
    storage.save_performers(filename, [Performer(1, "А", "поп", 5.0)])
    assert Path(filename).exists()


def test_save_writes_valid_utf8_json(tmp_path: Path) -> None:
    filename = str(tmp_path / "performers.json")
    storage.save_performers(filename, [Performer(1, "Мейби Бейби", "поп", 9.2)])
    with open(filename, encoding="utf-8") as file:
        data = json.load(file)
    assert data[0]["name"] == "Мейби Бейби"
