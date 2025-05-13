"""
Database schema definition for the LSB Music App.
"""

import sqlite3
import os
from pathlib import Path
import uuid
from datetime import datetime

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "lsb_catalogue.db"

# SQL statements for creating tables
CREATE_TABLES_SQL = """
-- Exercise Categories
CREATE TABLE IF NOT EXISTS exercise_categories (
    category_name TEXT PRIMARY KEY,    -- IBFexCATEGORY
    description TEXT                   -- Optional, for future expansion
);

-- Exercises
CREATE TABLE IF NOT EXISTS exercises (
    id TEXT PRIMARY KEY,               -- IBFex (can contain text like "14a")
    phase REAL,                        -- Phase
    category TEXT,                     -- IBFexCATEGORY
    name TEXT,                         -- IBFexNAME
    short_name TEXT,                   -- IBFexSHORT FORM NAME
    aka TEXT,                          -- AKA
    phase_reviewer TEXT,               -- Phase_reviewer
    FOREIGN KEY (category) REFERENCES exercise_categories(category_name)
);

-- Musics
CREATE TABLE IF NOT EXISTS musics (
    music_ref TEXT PRIMARY KEY,          -- MusicRef
    collection_cd TEXT,                  -- Music 'CD' (Genre tag)
    filename TEXT,                       -- Music filename
    title TEXT,                          -- Music Title (Movement Name tag)
    artist TEXT,                         -- Music Artist (Artist tag)
    duration TEXT,                       -- Time
    v INTEGER,                           -- V
    c INTEGER,                           -- C
    a INTEGER,                           -- A
    s INTEGER,                           -- S
    t INTEGER,                           -- T
    bpm INTEGER                          -- BPM
);

-- Exercise-to-Music mapping (Many-to-Many relationship)
CREATE TABLE IF NOT EXISTS exercise_music_mapping (
    exercise_id TEXT,                    -- IBFex (can contain text like "14a")
    music_ref TEXT,                      -- MusicRef
    recommendation TEXT,                 -- Recommendation
    specific_comment TEXT,               -- Exercise-Music specific comment
    PRIMARY KEY (exercise_id, music_ref),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id),
    FOREIGN KEY (music_ref) REFERENCES musics(music_ref)
);

-- Sessions table for storing metadata about saved sessions
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,                 -- UUID for the session
    name TEXT NOT NULL,                  -- Name of the session
    description TEXT,                    -- Description of the session
    date TEXT,                           -- Date of the session (YYYY-MM-DD)
    tags TEXT,                           -- Comma-separated tags (#tag format)
    created_at TEXT NOT NULL,            -- Creation timestamp
    updated_at TEXT NOT NULL,            -- Last update timestamp
    version INTEGER DEFAULT 1            -- Version for conflict detection
);

-- Session exercises for storing the exercises in a session with their order
CREATE TABLE IF NOT EXISTS session_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Auto-incrementing ID
    session_id TEXT,                      -- UUID of the parent session
    sequence_number INTEGER,              -- Order in the session
    exercise_id TEXT,                     -- Reference to the exercise
    music_ref TEXT,                       -- Reference to the selected music (nullable)
    notes TEXT,                           -- Notes for this exercise in the session
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id),
    FOREIGN KEY (music_ref) REFERENCES musics(music_ref)
);
"""


def init_db():
    """Initialize the database by creating required tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create tables
        cursor.executescript(CREATE_TABLES_SQL)

        conn.commit()
        print(f"Database initialized at {DB_PATH}")
        return True

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        return False

    finally:
        if conn:
            conn.close()


def get_db_connection():
    """Get a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = (
        sqlite3.Row
    )  # This enables column access by name: row['column_name']
    return conn


if __name__ == "__main__":
    # Initialize the database when this module is run directly
    init_db()
