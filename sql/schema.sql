-- Concerty SQLite schema (ПР7). Raw sqlite3, Django ORM is NOT used.
-- Concert fields mirror src/models/concerts.py; dates are TEXT in ISO format,
-- is_cancelled is INTEGER 0/1.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS performers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    genre TEXT NOT NULL,
    rating REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS venues (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    capacity INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    duration INTEGER NOT NULL,
    age_limit INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS concerts (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    performer_id INTEGER NOT NULL,
    venue_id INTEGER NOT NULL,
    program_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    expected_guests INTEGER NOT NULL,
    base_ticket_price REAL NOT NULL,
    is_cancelled INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (performer_id) REFERENCES performers (id),
    FOREIGN KEY (venue_id) REFERENCES venues (id),
    FOREIGN KEY (program_id) REFERENCES programs (id)
);
