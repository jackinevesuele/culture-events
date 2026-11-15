CREATE TABLE interests (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE visitors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL CHECK (age BETWEEN 0 AND 120),
    budget NUMERIC NOT NULL CHECK (budget >= 0)
);
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    price NUMERIC NOT NULL CHECK (price >= 0),
    min_age INTEGER NOT NULL CHECK (min_age BETWEEN 0 AND 120),
    active INTEGER NOT NULL CHECK (active IN (0, 1))
);
CREATE TABLE visitor_interests (
    visitor_id INTEGER NOT NULL REFERENCES visitors(id) ON DELETE CASCADE,
    interest_id INTEGER NOT NULL REFERENCES interests(id) ON DELETE CASCADE,
    PRIMARY KEY (visitor_id, interest_id)
);
CREATE TABLE event_interests (
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    interest_id INTEGER NOT NULL REFERENCES interests(id) ON DELETE CASCADE,
    PRIMARY KEY (event_id, interest_id)
);
CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY,
    visitor_id INTEGER NOT NULL REFERENCES visitors(id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score > 0),
    status TEXT NOT NULL CHECK (status IN ('new', 'dismissed')),
    UNIQUE (visitor_id, event_id)
);
CREATE INDEX events_date ON events(active, date);
