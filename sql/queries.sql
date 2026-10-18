-- Concerty SQL queries (ПР7). Each query is CLI-verified against
-- data/concerty.sqlite, e.g.:
--   sqlite3 data/concerty.sqlite < sql/queries.sql
-- Values from users MUST be passed via ? placeholders, never f-strings.

-- Q01. Plain list: all performers ordered by rating (highest first).
SELECT id, name, genre, rating
FROM performers
ORDER BY rating DESC;

-- Q02. Plain list: all venues ordered by capacity.
SELECT id, name, city, capacity
FROM venues
ORDER BY capacity DESC;

-- Q03. WHERE filter: venues with capacity at least ? guests.
SELECT id, name, city, capacity
FROM venues
WHERE capacity >= ?
ORDER BY capacity;

-- Q04. WHERE filter: concerts scheduled from date ? onwards.
SELECT id, title, date, expected_guests, is_cancelled
FROM concerts
WHERE date >= ?
ORDER BY date;

-- Q05. WHERE filter: active (not cancelled) concerts.
SELECT id, title, date, expected_guests
FROM concerts
WHERE is_cancelled = 0
ORDER BY date;

-- Q06. JOIN detail: concert with performer, venue and program names.
SELECT c.id, c.title, c.date, p.name AS performer,
       v.name AS venue, pr.name AS program,
       c.expected_guests, c.base_ticket_price, c.is_cancelled
FROM concerts c
JOIN performers p ON p.id = c.performer_id
JOIN venues v ON v.id = c.venue_id
JOIN programs pr ON pr.id = c.program_id
WHERE c.id = ?;

-- Q07. JOIN detail: all concerts with related names, soonest first.
SELECT c.id, c.title, c.date, p.name AS performer,
       v.name AS venue, pr.name AS program, c.is_cancelled
FROM concerts c
JOIN performers p ON p.id = c.performer_id
JOIN venues v ON v.id = c.venue_id
JOIN programs pr ON pr.id = c.program_id
ORDER BY c.date;

-- Q08. Availability by date: venues free on date ? (not cancelled).
-- Mirrors Concert.blocks_venue(): cancelled concerts do not block.
SELECT v.id, v.name, v.city, v.capacity
FROM venues v
LEFT JOIN concerts c
  ON c.venue_id = v.id AND c.date = ? AND c.is_cancelled = 0
WHERE c.id IS NULL
ORDER BY v.name;

-- Q09. Availability by date: concerts blocking venue ? on date ?.
SELECT c.id, c.title, c.date
FROM concerts c
WHERE c.venue_id = ? AND c.date = ? AND c.is_cancelled = 0;

-- Q10. Aggregate: total number of concerts.
SELECT COUNT(*) AS concert_count
FROM concerts;

-- Q11. Statistics: cancelled vs active concerts and guest sums.
SELECT is_cancelled,
       COUNT(*) AS concert_count,
       SUM(expected_guests) AS total_guests
FROM concerts
GROUP BY is_cancelled;

-- Q12. GROUP BY: number of concerts per venue.
SELECT v.id, v.name, COUNT(c.id) AS concert_count
FROM venues v
LEFT JOIN concerts c ON c.venue_id = v.id
GROUP BY v.id, v.name
ORDER BY concert_count DESC, v.name;

-- Q13. GROUP BY + HAVING: venues hosting more than ? concerts.
SELECT v.id, v.name, COUNT(c.id) AS concert_count
FROM venues v
JOIN concerts c ON c.venue_id = v.id
GROUP BY v.id, v.name
HAVING COUNT(c.id) > ?
ORDER BY concert_count DESC;
