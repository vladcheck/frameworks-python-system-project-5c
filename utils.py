"""Вспомогательные функции безопасного ввода данных."""

from datetime import date

DATE_FORMAT = "%d.%m.%Y"


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число, повторяя запрос при ошибке."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число")


def input_date(prompt: str) -> date:
    """Запросить у пользователя дату в формате ДД.ММ.ГГГГ."""
    while True:
        try:
            return date.strptime(input(prompt), DATE_FORMAT)
        except ValueError:
            print("Ошибка: введите дату в формате ДД.ММ.ГГГГ")
