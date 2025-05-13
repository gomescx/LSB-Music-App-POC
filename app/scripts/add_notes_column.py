#!/usr/bin/env python3
"""
Migration script to add the notes column to the session_exercises table.
"""

import sys
import sqlite3
import os
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.db.schema import DB_PATH


def add_notes_column():
    """
    Add a 'notes' column to the session_exercises table if it doesn't exist.
    """
    print(f"Connecting to database at {DB_PATH}...")

    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return False

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check if notes column exists
        cursor.execute("PRAGMA table_info(session_exercises)")
        columns = cursor.fetchall()
        column_names = [col["name"] for col in columns]

        if "notes" in column_names:
            print("Notes column already exists in session_exercises table.")
            return True

        # Add the notes column
        print("Adding notes column to session_exercises table...")
        cursor.execute("ALTER TABLE session_exercises ADD COLUMN notes TEXT;")
        conn.commit()

        print("Migration completed successfully.")
        return True

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    success = add_notes_column()
    sys.exit(0 if success else 1)
