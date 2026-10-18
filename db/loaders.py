"""Load Concerty model objects from SQLite (raw sqlite3, no Django ORM).

All SQL here uses ? placeholders; f-string SQL is never used.
If the SQLite file is absent, loaders raise FileNotFoundError so callers
(Django views) can gracefully fall back to JSON storage.
"""

from datetime import date

from db.database import connect, get_db_path
from src.models import Concert, Performer, Program, Venue
from src.models.performers import get_performer_by_id
from src.models.programs import get_program_by_id
from src.models.venues import get_venue_by_id


def sqlite_available() -> bool:
    """Return True when the data/concerty.sqlite file exists."""
    return get_db_path().exists()


def _require_db() -> None:
    if not sqlite_available():
        raise FileNotFoundError(f"SQLite file not found: {get_db_path()}")


def load_all() -> tuple[
    list[Performer], list[Venue], list[Program], list[Concert]
]:
    """Load all objects from SQLite, rebuilding Concert links by id."""
    _require_db()
    conn = connect()
    try:
        performers = [
            Performer(
                row["id"], row["name"], row["genre"], row["rating"]
            )
            for row in conn.execute(
                "SELECT id, name, genre, rating FROM performers ORDER BY id;"
            )
        ]
        venues = [
            Venue(row["id"], row["name"], row["city"], row["capacity"])
            for row in conn.execute(
                "SELECT id, name, city, capacity FROM venues ORDER BY id;"
            )
        ]
        programs = [
            Program(
                row["id"], row["name"], row["duration"], row["age_limit"]
            )
            for row in conn.execute(
                "SELECT id, name, duration, age_limit"
                " FROM programs ORDER BY id;"
            )
        ]
        concerts = []
        rows = conn.execute(
            "SELECT id, title, performer_id, venue_id, program_id, date,"
            " expected_guests, base_ticket_price, is_cancelled"
            " FROM concerts ORDER BY id;"
        )
        for row in rows:
            performer = get_performer_by_id(performers, row["performer_id"])
            venue = get_venue_by_id(venues, row["venue_id"])
            program = get_program_by_id(programs, row["program_id"])
            if performer is None or venue is None or program is None:
                continue
            concert = Concert(
                row["id"],
                row["title"],
                performer,
                venue,
                program,
                date.fromisoformat(row["date"]),
                row["expected_guests"],
                row["base_ticket_price"],
            )
            concert.is_cancelled = bool(row["is_cancelled"])
            concerts.append(concert)
        return performers, venues, programs, concerts
    finally:
        conn.close()


def venue_free_on(venue_id: int, check_date: date) -> bool:
    """Check via SQLite that a venue has no active concert on a date.

    Mirrors Concert.blocks_venue(): cancelled concerts do not block.
    """
    _require_db()
    conn = connect()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS busy FROM concerts"
            " WHERE venue_id = ? AND date = ? AND is_cancelled = 0;",
            (venue_id, check_date.isoformat()),
        ).fetchone()
        return row["busy"] == 0
    finally:
        conn.close()
