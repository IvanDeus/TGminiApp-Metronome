-- schema.sql

DROP TABLE IF EXISTS telegram_users;

CREATE TABLE telegram_users (
    user_id INTEGER PRIMARY KEY,
    telegram_id INTEGER DEFAULT NULL,
    is_bot BOOLEAN DEFAULT 0,
    first_name TEXT NOT NULL,
    last_name TEXT,
    username TEXT,
    language_code TEXT,
    is_premium BOOLEAN DEFAULT 0,
    photo_url TEXT,
    bpm INTEGER DEFAULT 90,
    is_subbed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
