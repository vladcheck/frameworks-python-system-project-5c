"""Тесты функций безопасного ввода из модуля utils."""

from datetime import date

from src import utils


def test_input_int_happy_path(monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt="": "42")
    assert utils.input_int("Число: ") == 42


def test_input_int_retries_on_invalid(monkeypatch, capsys) -> None:
    answers = iter(["abc", "3.5", "7"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    assert utils.input_int("Число: ") == 7
    assert capsys.readouterr().out.count("Ошибка: введите целое число") == 2


def test_input_int_accepts_negative(monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt="": "-5")
    assert utils.input_int("Число: ") == -5


def test_input_date_happy_path(monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt="": "15.10.2026")
    assert utils.input_date("Дата: ") == date(2026, 10, 15)


def test_input_date_retries_on_invalid(monkeypatch, capsys) -> None:
    answers = iter(["2026-10-15", "не дата", "01.01.2027"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    assert utils.input_date("Дата: ") == date(2027, 1, 1)
    assert "Ошибка: введите дату" in capsys.readouterr().out


def test_input_date_leap_day(monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt="": "29.02.2024")
    assert utils.input_date("Дата: ") == date(2024, 2, 29)


def test_input_date_rejects_invalid_day(monkeypatch) -> None:
    answers = iter(["31.02.2026", "28.02.2026"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    assert utils.input_date("Дата: ") == date(2026, 2, 28)
