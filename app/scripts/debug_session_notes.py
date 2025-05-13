#!/usr/bin/env python3
"""
Debug script to examine session data loaded from the database.
"""

import sys
import sqlite3
import os
from pathlib import Path
import pprint

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.db.schema import get_db_connection, DB_PATH
from app.db.queries import get_session_by_id, get_all_sessions


def debug_session_load():
    """
    Debug function to examine if notes are loaded correctly.
    """
    print(f"Connecting to database at {DB_PATH}...")

    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return False

    # Get all sessions
    sessions = get_all_sessions()

    if not sessions:
        print("No sessions found in the database.")
        return False

    # Print available sessions
    print("\nAvailable sessions:")
    for i, session in enumerate(sessions):
        print(f"{i+1}. {session['name']} (ID: {session['id']})")

    # Choose the first session to debug
    session_id = sessions[0]["id"]
    print(f"\nDebugging session: {sessions[0]['name']} (ID: {session_id})")

    # Load the session
    session_data, session_exercises = get_session_by_id(session_id)

    # Print session metadata
    print("\nSession metadata:")
    pprint.pprint(session_data)

    # Print session exercises
    print("\nSession exercises:")
    for i, exercise in enumerate(session_exercises):
        print(f"\nExercise {i+1}:")
        print(f"  Name: {exercise[0]}")
        print(f"  Music Ref: {exercise[1]}")
        print(f"  Exercise ID: {exercise[2]}")
        print(f"  Notes: {repr(exercise[3] if len(exercise) >= 4 else 'N/A')}")

    # Directly query the database to check raw notes values
    print("\nDirect database query for notes:")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT sequence_number, exercise_id, notes
            FROM session_exercises
            WHERE session_id = ?
            ORDER BY sequence_number
            """,
            (session_id,),
        )
        results = cursor.fetchall()

        for row in results:
            # Use more robust method to access columns
            try:
                notes = row["notes"] if row["notes"] is not None else ""
            except (IndexError, KeyError):
                notes = "N/A"

            print(
                f"Seq #{row['sequence_number']} | Exercise ID: {row['exercise_id']} | Notes: {repr(notes)}"
            )

    except sqlite3.Error as e:
        print(f"Error querying database: {e}")
    finally:
        conn.close()

    return True


if __name__ == "__main__":
    debug_session_load()
