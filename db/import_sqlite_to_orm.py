"""Перенос данных из базы ПР7 (sqlite3) в таблицы Django ORM.

Скрипт читает исходную базу data/concerty.sqlite, не изменяя её,
и создаёт записи моделей Performer, Venue, Program и Concert
в целевой базе Django (db.sqlite3). Запуск после миграций:

    python db/import_sqlite_to_orm.py
"""

import os
import sqlite3
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import django
from django.db import transaction

# Корень проекта: скрипт лежит в каталоге db.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Модуль настроек Django проекта Concerty.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "concerty.settings",
)

# Инициализация Django до импорта моделей.
django.setup()

from concerts.models import Concert  # noqa: E402
from performers.models import Performer  # noqa: E402
from programs.models import Program  # noqa: E402
from venues.models import Venue  # noqa: E402

SOURCE_DB = BASE_DIR / "data" / "concerty.sqlite"


def read_source() -> tuple[list[sqlite3.Row], ...]:
    """Прочитать все записи исходной базы (только чтение)."""
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {SOURCE_DB}")

    with sqlite3.connect(SOURCE_DB) as connection:
        connection.row_factory = sqlite3.Row
        performers = connection.execute(
            "SELECT id, name, genre, rating FROM performers ORDER BY id;"
        ).fetchall()
        venues = connection.execute(
            "SELECT id, name, city, capacity FROM venues ORDER BY id;"
        ).fetchall()
        programs = connection.execute(
            "SELECT id, name, duration, age_limit FROM programs ORDER BY id;"
        ).fetchall()
        concerts = connection.execute(
            "SELECT id, title, performer_id, venue_id, program_id, date,"
            " expected_guests, base_ticket_price, is_cancelled"
            " FROM concerts ORDER BY id;"
        ).fetchall()
    return performers, venues, programs, concerts


def transfer() -> dict[str, int]:
    """Перенести данные в целевые таблицы одной транзакцией."""
    performers, venues, programs, concerts = read_source()

    with transaction.atomic():
        # Сначала независимые справочники: на них ссылаются концерты.
        for row in performers:
            Performer.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "genre": row["genre"],
                    "rating": Decimal(str(row["rating"])),
                },
            )
        for row in venues:
            Venue.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "city": row["city"],
                    "capacity": row["capacity"],
                },
            )
        for row in programs:
            Program.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "duration": row["duration"],
                    "age_limit": row["age_limit"],
                },
            )
        # Затем концерты: внешние ключи ссылаются на готовые записи.
        for row in concerts:
            Concert.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "title": row["title"],
                    "performer_id": row["performer_id"],
                    "venue_id": row["venue_id"],
                    "program_id": row["program_id"],
                    "date": date.fromisoformat(row["date"]),
                    "expected_guests": row["expected_guests"],
                    "base_ticket_price": Decimal(
                        str(row["base_ticket_price"])
                    ),
                    "is_cancelled": bool(row["is_cancelled"]),
                },
            )

    return {
        "Исполнители": Performer.objects.count(),
        "Площадки": Venue.objects.count(),
        "Программы": Program.objects.count(),
        "Концерты": Concert.objects.count(),
    }


def main() -> None:
    """Выполнить перенос и вывести количество записей в целевой базе."""
    counts = transfer()
    print("Перенос данных завершён.")
    for name, count in counts.items():
        print(f"{name}: {count}")


if __name__ == "__main__":
    main()
