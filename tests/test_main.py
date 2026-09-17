"""Тесты точки входа: загрузка и сохранение всех данных."""

import json
from datetime import date
from pathlib import Path

from src import main
from src.models import Concert, Performer, Program, Venue


def patch_data_files(monkeypatch, tmp_path: Path) -> None:
    """Перенаправить пути к JSON-файлам во временный каталог."""
    monkeypatch.setattr(main, "PERFORMERS_FILE", str(tmp_path / "performers.json"))
    monkeypatch.setattr(main, "VENUES_FILE", str(tmp_path / "venues.json"))
    monkeypatch.setattr(main, "PROGRAMS_FILE", str(tmp_path / "programs.json"))
    monkeypatch.setattr(main, "CONCERTS_FILE", str(tmp_path / "concerts.json"))


def test_load_all_data_missing_files(monkeypatch, tmp_path: Path) -> None:
    patch_data_files(monkeypatch, tmp_path)
    performers, venues, programs, concerts = main.load_all_data()
    assert performers == []
    assert venues == []
    assert programs == []
    assert concerts == []


def test_save_and_load_all_data_round_trip(monkeypatch, tmp_path: Path) -> None:
    patch_data_files(monkeypatch, tmp_path)
    performer = Performer(1, "Мейби Бейби", "гиперпоп", 9.2)
    venue = Venue(1, "Adrenaline Stadium", "Москва", 5000)
    program = Program(1, "MAYDAY", 90, 16)
    concert = Concert(
        concert_id=1,
        title="Клубный вечер",
        performer=performer,
        venue=venue,
        program=program,
        concert_date=date(2026, 10, 15),
        expected_guests=4800,
        base_ticket_price=2500.0,
    )
    data = ([performer], [venue], [program], [concert])
    main.save_all_data(*data)
    loaded = main.load_all_data()
    assert [p.to_data() for p in loaded[0]] == [performer.to_data()]
    assert [v.to_data() for v in loaded[1]] == [venue.to_data()]
    assert [p.to_data() for p in loaded[2]] == [program.to_data()]
    assert [c.to_data() for c in loaded[3]] == [concert.to_data()]


def test_main_runs_menu_and_saves(monkeypatch, tmp_path: Path) -> None:
    patch_data_files(monkeypatch, tmp_path)
    (tmp_path / "performers.json").write_text(
        json.dumps([{"id": 1, "name": "А", "genre": "поп", "rating": 7.0}]),
        encoding="utf-8",
    )
    monkeypatch.setattr("builtins.input", lambda prompt="": "0")
    main.main()
    assert (tmp_path / "performers.json").exists()
