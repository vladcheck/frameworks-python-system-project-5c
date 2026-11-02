"""Просмотр структуры исходной базы ПР7 data/concerty.sqlite.

Скрипт выполняет только запросы на чтение и не изменяет базу:

    python db/inspect_source_db.py
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DB = BASE_DIR / "data" / "concerty.sqlite"


def main() -> None:
    """Вывести таблицы, столбцы и количество записей исходной базы."""
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {SOURCE_DB}")

    with sqlite3.connect(SOURCE_DB) as connection:
        connection.row_factory = sqlite3.Row
        tables = connection.execute(
            "SELECT name FROM sqlite_master"
            " WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            " ORDER BY name;"
        ).fetchall()
        for (table_name,) in tables:
            print(f"\nТаблица: {table_name}")
            for column in connection.execute(
                f'PRAGMA table_info("{table_name}");'
            ).fetchall():
                print(
                    f"  имя={column['name']}, тип={column['type']},"
                    f" NOT NULL={column['notnull']},"
                    f" PRIMARY KEY={column['pk']}"
                )
            count = connection.execute(
                f'SELECT COUNT(*) FROM "{table_name}";'
            ).fetchone()[0]
            print(f"  Количество записей: {count}")


if __name__ == "__main__":
    main()
