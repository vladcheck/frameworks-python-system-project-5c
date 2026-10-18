"""Tests for the raw-sqlite3 storage layer (ПР7, no Django ORM)."""

import json
import sqlite3
from datetime import date
from pathlib import Path

from db import database, loaders
from db.database import connect
from db.import_json import create_schema, import_all
from db.loaders import load_all, venue_free_on


def _memdb() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    schema = Path("sql/schema.sql").read_text(encoding="utf-8")
    conn.executescript(schema)
    return conn


def _json_counts() -> dict[str, int]:
    counts = {}
    for name in ("performers", "venues", "programs", "concerts"):
        data = json.loads(Path(f"data/{name}.json").read_text(encoding="utf-8"))
        counts[name] = len(data)
    return counts


def test_schema_creates_four_tables():
    conn = _memdb()
    try:
        tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table';"
            )
        }
        assert {"performers", "venues", "programs", "concerts"} <= tables
        cols = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(concerts);")
        }
        assert {
            "id", "title", "performer_id", "venue_id", "program_id",
            "date", "expected_guests", "base_ticket_price", "is_cancelled",
        } <= cols
        assert conn.execute("PRAGMA foreign_key_list(concerts);").fetchall()
    finally:
        conn.close()


def test_import_counts_match_json():
    conn = _memdb()
    try:
        counts = import_all(conn)
        assert counts == _json_counts()
        for table, expected in counts.items():
            row = conn.execute(f"SELECT COUNT(*) AS n FROM {table};").fetchone()
            assert row["n"] == expected
    finally:
        conn.close()


def test_import_is_idempotent():
    conn = _memdb()
    try:
        first = import_all(conn)
        second = import_all(conn)
        assert first == second
        for table, expected in first.items():
            row = conn.execute(f"SELECT COUNT(*) AS n FROM {table};").fetchone()
            assert row["n"] == expected
    finally:
        conn.close()


def test_join_detail_returns_expected_row():
    conn = _memdb()
    try:
        import_all(conn)
        row = conn.execute(
            "SELECT c.title, p.name AS performer, v.name AS venue,"
            " pr.name AS program FROM concerts c"
            " JOIN performers p ON p.id = c.performer_id"
            " JOIN venues v ON v.id = c.venue_id"
            " JOIN programs pr ON pr.id = c.program_id"
            " WHERE c.id = ?;",
            (1,),
        ).fetchone()
        assert row["title"] == "Клубный вечер с Мейби Бейби"
        assert row["performer"] == "Мейби Бейби"
        assert row["venue"] == "Adrenaline Stadium"
        assert row["program"] == "MAYDAY: клубный сет"
    finally:
        conn.close()


def test_availability_query_matches_model():
    conn = _memdb()
    try:
        import_all(conn)
        busy_date = conn.execute(
            "SELECT venue_id, date FROM concerts"
            " WHERE is_cancelled = 0 ORDER BY date LIMIT 1;"
        ).fetchone()
        assert busy_date is not None
        free = conn.execute(
            "SELECT v.id FROM venues v LEFT JOIN concerts c ON c.venue_id"
            " = v.id AND c.date = ? AND c.is_cancelled = 0"
            " WHERE c.id IS NULL;",
            (busy_date["date"],),
        ).fetchall()
        assert all(r["id"] != busy_date["venue_id"] for r in free)
        assert len(free) == 11
    finally:
        conn.close()


def test_statistics_group_by_status():
    conn = _memdb()
    try:
        counts = import_all(conn)
        rows = conn.execute(
            "SELECT is_cancelled, COUNT(*) AS n,"
            " SUM(expected_guests) AS guests FROM concerts"
            " GROUP BY is_cancelled;"
        ).fetchall()
        total = sum(r["n"] for r in rows)
        assert total == counts["concerts"]
        json_guests = sum(
            c["expected_guests"]
            for c in json.loads(
                Path("data/concerts.json").read_text(encoding="utf-8")
            )
        )
        assert sum(r["guests"] for r in rows) == json_guests
    finally:
        conn.close()


def test_loaders_and_availability_use_placeholders(tmp_path, monkeypatch):
    db_path = tmp_path / "test.sqlite"
    monkeypatch.setattr(loaders, "get_db_path", lambda: db_path)
    monkeypatch.setattr(database, "get_db_path", lambda: db_path)
    conn = connect(db_path)
    try:
        create_schema(conn)
        import_all(conn)
    finally:
        conn.close()
    assert loaders.get_db_path() == db_path
    performers, venues, programs, concerts = load_all()
    expected = _json_counts()
    assert len(performers) == expected["performers"]
    assert len(venues) == expected["venues"]
    assert len(programs) == expected["programs"]
    assert len(concerts) == expected["concerts"]
    first = concerts[0]
    assert first.performer.name == "Мейби Бейби"
    assert first.venue.name == "Adrenaline Stadium"
    assert first.program.name == "MAYDAY: клубный сет"
    assert isinstance(first.date, date)
    assert not venue_free_on(first.venue.id, first.date)
    assert venue_free_on(first.venue.id, date(1999, 1, 1))
    source = Path("db/loaders.py").read_text(encoding="utf-8")
    assert 'f"SELECT' not in source
    assert "f'SELECT" not in source
