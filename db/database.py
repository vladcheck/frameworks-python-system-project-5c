"""SQLite connection helper (raw sqlite3, Django ORM is NOT used)."""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILENAME = "concerty.sqlite"


def get_db_path() -> Path:
    """Return the path of the Concerty SQLite file (data/concerty.sqlite).

    This file is separate from Django's db.sqlite3 database.
    """
    return BASE_DIR / "data" / DB_FILENAME


def connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Open a SQLite connection with Row access and enabled FK checks."""
    path = Path(db_path) if db_path is not None else get_db_path()
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
