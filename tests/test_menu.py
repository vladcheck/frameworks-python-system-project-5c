"""Тесты консольного меню: вывод списков и обработчики пунктов."""

from datetime import date

from src.menu import (
    menu_add_concert,
    menu_cancel_concert,
    menu_check_venue,
    menu_filter_venues,
    menu_find_concert,
    menu_find_venue,
    menu_show_concerts,
    menu_show_venues,
    menu_statistics,
    run_menu,
    show_concerts,
    show_venues,
)
from src.models import Concert, Performer, Program, Venue


def make_data() -> tuple[list[Performer], list[Venue], list[Program], list[Concert]]:
    """Подготовить тестовый набор коллекций для меню."""
    performer = Performer(1, "Мейби Бейби", "гиперпоп", 9.2)
    venue = Venue(1, "Adrenaline Stadium", "Москва", 5000)
    program = Program(1, "MAYDAY", 90, 16)
    concert = Concert(
        concert_id=1,
        title="Клубный вечер",
        performer=performer,
        venue=venue,
        program=program,
        concert_date=date(2999, 10, 15),
        expected_guests=4800,
        base_ticket_price=2500.0,
    )
    return [performer], [venue], [program], [concert]


def test_show_concerts_empty(capsys) -> None:
    show_concerts([])
    assert "Концерты не найдены" in capsys.readouterr().out


def test_show_concerts_prints_details(capsys) -> None:
    _, _, _, concerts = make_data()
    show_concerts(concerts)
    out = capsys.readouterr().out
    assert "1. Клубный вечер" in out
    assert "Мейби Бейби" in out
    assert "Adrenaline Stadium" in out
    assert "MAYDAY" in out


def test_show_venues_empty(capsys) -> None:
    show_venues([])
    assert "Площадки не найдены" in capsys.readouterr().out


def test_show_venues_prints_list(capsys) -> None:
    _, venues, _, _ = make_data()
    show_venues(venues)
    out = capsys.readouterr().out
    assert "1. Adrenaline Stadium" in out
    assert "5000 мест" in out


def test_menu_show_concerts(capsys) -> None:
    data = make_data()
    menu_show_concerts(data)
    assert "Клубный вечер" in capsys.readouterr().out


def test_menu_find_concert_found(monkeypatch, capsys) -> None:
    data = make_data()
    monkeypatch.setattr("builtins.input", lambda prompt="": "клубн")
    menu_find_concert(data)
    assert "Клубный вечер" in capsys.readouterr().out


def test_menu_find_concert_not_found(monkeypatch, capsys) -> None:
    data = make_data()
    monkeypatch.setattr("builtins.input", lambda prompt="": "симфония")
    menu_find_concert(data)
    assert "Концерты не найдены" in capsys.readouterr().out


def test_menu_show_venues(capsys) -> None:
    data = make_data()
    menu_show_venues(data)
    assert "Adrenaline Stadium" in capsys.readouterr().out


def test_menu_find_venue_found(monkeypatch, capsys) -> None:
    data = make_data()
    monkeypatch.setattr("builtins.input", lambda prompt="": "adrenaline")
    menu_find_venue(data)
    assert "Adrenaline Stadium" in capsys.readouterr().out


def test_menu_find_venue_not_found(monkeypatch, capsys) -> None:
    data = make_data()
    monkeypatch.setattr("builtins.input", lambda prompt="": "космонавт")
    menu_find_venue(data)
    assert "Площадки не найдены" in capsys.readouterr().out


def test_menu_check_venue_available(monkeypatch, capsys) -> None:
    data = make_data()
    answers = iter(["1", "20.10.2999"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    menu_check_venue(data)
    assert "Площадка свободна" in capsys.readouterr().out


def test_menu_check_venue_busy(monkeypatch, capsys) -> None:
    data = make_data()
    answers = iter(["1", "15.10.2999"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    menu_check_venue(data)
    assert "Площадка занята" in capsys.readouterr().out


def test_menu_cancel_concert_found(monkeypatch, capsys) -> None:
    data = make_data()
    monkeypatch.setattr("builtins.input", lambda prompt="": "1")
    menu_cancel_concert(data)
    assert "Концерт отменен" in capsys.readouterr().out
    assert data[3][0].is_cancelled


def test_menu_cancel_concert_not_found(monkeypatch, capsys) -> None:
    data = make_data()
    monkeypatch.setattr("builtins.input", lambda prompt="": "99")
    menu_cancel_concert(data)
    assert "концерт не найден" in capsys.readouterr().out


def test_menu_filter_venues(monkeypatch, capsys) -> None:
    data = make_data()
    monkeypatch.setattr("builtins.input", lambda prompt="": "5000")
    menu_filter_venues(data)
    assert "Adrenaline Stadium" in capsys.readouterr().out


def test_menu_filter_venues_no_match(monkeypatch, capsys) -> None:
    data = make_data()
    monkeypatch.setattr("builtins.input", lambda prompt="": "10000")
    menu_filter_venues(data)
    assert "Площадки не найдены" in capsys.readouterr().out


def test_menu_add_concert_happy_path(monkeypatch, capsys) -> None:
    data = make_data()
    answers = iter(["Новый концерт", "1", "1", "1", "20.10.2999", "100"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    menu_add_concert(data)
    assert "Концерт добавлен" in capsys.readouterr().out
    assert len(data[3]) == 2
    assert data[3][1].title == "Новый концерт"


def test_menu_add_concert_performer_not_found(monkeypatch, capsys) -> None:
    data = make_data()
    monkeypatch.setattr("builtins.input", lambda prompt="": "99")
    menu_add_concert(data)
    assert "исполнитель не найден" in capsys.readouterr().out
    assert len(data[3]) == 1


def test_menu_add_concert_venue_not_found(monkeypatch, capsys) -> None:
    data = make_data()
    answers = iter(["Новый концерт", "1", "99"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    menu_add_concert(data)
    assert "площадка не найдена" in capsys.readouterr().out
    assert len(data[3]) == 1


def test_menu_add_concert_program_not_found(monkeypatch, capsys) -> None:
    data = make_data()
    answers = iter(["Новый концерт", "1", "1", "99"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    menu_add_concert(data)
    assert "программа не найдена" in capsys.readouterr().out
    assert len(data[3]) == 1


def test_menu_add_concert_venue_busy(monkeypatch, capsys) -> None:
    data = make_data()
    answers = iter(["Новый концерт", "1", "1", "1", "15.10.2999", "100"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    menu_add_concert(data)
    assert "площадка занята" in capsys.readouterr().out
    assert len(data[3]) == 1


def test_menu_add_concert_too_many_guests(monkeypatch, capsys) -> None:
    data = make_data()
    answers = iter(["Новый концерт", "1", "1", "1", "20.10.2999", "5001"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    menu_add_concert(data)
    assert "не вмещает всех зрителей" in capsys.readouterr().out
    assert len(data[3]) == 1


def test_menu_statistics(capsys) -> None:
    data = make_data()
    menu_statistics(data)
    out = capsys.readouterr().out
    assert "Запланировано концертов: 1" in out
    assert "Ожидается зрителей: 4800" in out


def test_run_menu_valid_choice_then_exit(monkeypatch, capsys) -> None:
    answers = iter(["3", "0"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    run_menu(make_data())
    assert "Adrenaline Stadium" in capsys.readouterr().out


def test_run_menu_invalid_choice_then_exit(monkeypatch, capsys) -> None:
    answers = iter(["42", "0"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    run_menu(make_data())
    assert "Неверное действие" in capsys.readouterr().out
