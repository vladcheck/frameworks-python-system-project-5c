"""Import JSON data into SQLite (runnable as ``python -m db.import_json``)."""

import sqlite3
from pathlib import Path

from db.database import connect, get_db_path
from src.storage import (
    load_concerts,
    load_performers,
    load_programs,
    load_venues,
)

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def create_schema(conn: sqlite3.Connection) -> None:
    """Create tables from sql/schema.sql."""
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def import_all(conn: sqlite3.Connection) -> dict[str, int]:
    """Load JSON files via src.storage loaders and reinsert rows.

    Idempotent: existing rows are deleted before reinsertion, so repeated
    runs produce the same database state. Child table (concerts) is cleared
    first to satisfy FOREIGN KEY constraints.
    """
    base = BASE_DIR / "data"
    performers = load_performers(str(base / "performers.json"))
    venues = load_venues(str(base / "venues.json"))
    programs = load_programs(str(base / "programs.json"))
    concerts = load_concerts(
        str(base / "concerts.json"), performers, venues, programs
    )

    conn.execute("DELETE FROM concerts;")
    conn.execute("DELETE FROM performers;")
    conn.execute("DELETE FROM venues;")
    conn.execute("DELETE FROM programs;")

    conn.executemany(
        "INSERT OR REPLACE INTO performers (id, name, genre, rating)"
        " VALUES (?, ?, ?, ?);",
        [(p.id, p.name, p.genre, p.rating) for p in performers],
    )
    conn.executemany(
        "INSERT OR REPLACE INTO venues (id, name, city, capacity)"
        " VALUES (?, ?, ?, ?);",
        [(v.id, v.name, v.city, v.capacity) for v in venues],
    )
    conn.executemany(
        "INSERT OR REPLACE INTO programs (id, name, duration, age_limit)"
        " VALUES (?, ?, ?, ?);",
        [(p.id, p.name, p.duration, p.age_limit) for p in programs],
    )
    conn.executemany(
        "INSERT OR REPLACE INTO concerts (id, title, performer_id, venue_id,"
        " program_id, date, expected_guests, base_ticket_price, is_cancelled)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
        [
            (
                c.id,
                c.title,
                c.performer.id,
                c.venue.id,
                c.program.id,
                c.date.isoformat(),
                c.expected_guests,
                c.base_ticket_price,
                1 if c.is_cancelled else 0,
            )
            for c in concerts
        ],
    )
    conn.commit()
    return {
        "performers": len(performers),
        "venues": len(venues),
        "programs": len(programs),
        "concerts": len(concerts),
    }


def main() -> None:
    """Create the schema and import all JSON files into data/concerty.sqlite."""
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(path)
    try:
        create_schema(conn)
        counts = import_all(conn)
    finally:
        conn.close()
    for table, count in counts.items():
        print(f"{table}: {count}")


if __name__ == "__main__":
    main()
