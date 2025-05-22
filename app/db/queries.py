"""
Database query functions for the LSB Music App.
"""

import sqlite3
import uuid
from datetime import datetime
from .schema import get_db_connection


def insert_exercise_categories(categories):
    """Insert exercise categories into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.executemany(
            "INSERT OR REPLACE INTO exercise_categories (category_name) VALUES (?)",
            [(category,) for category in categories],
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error inserting exercise categories: {e}")
    finally:
        conn.close()


def insert_exercises(exercises):
    """
    Insert exercises into the database.

    Args:
        exercises: List of dicts with keys matching the exercises table columns
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.executemany(
            """
            INSERT OR REPLACE INTO exercises 
            (id, phase, category, name, short_name, aka, phase_reviewer) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    ex["id"],
                    ex["phase"],
                    ex["category"],
                    ex["name"],
                    ex["short_name"],
                    ex["aka"],
                    ex["phase_reviewer"],
                )
                for ex in exercises
            ],
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error inserting exercises: {e}")
    finally:
        conn.close()


def insert_musics(musics):
    """
    Insert music records into the database.

    Args:
        musics: List of dicts with keys matching the musics table columns
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.executemany(
            """
            INSERT OR REPLACE INTO musics 
            (music_ref, collection_cd, filename, title, artist, duration, 
             v, c, a, s, t, bpm) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    m["music_ref"],
                    m["collection_cd"],
                    m["filename"],
                    m["title"],
                    m["artist"],
                    m["duration"],
                    m["v"],
                    m["c"],
                    m["a"],
                    m["s"],
                    m["t"],
                    m["bpm"],
                )
                for m in musics
            ],
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error inserting musics: {e}")
    finally:
        conn.close()


def insert_exercise_music_mappings(mappings):
    """
    Insert exercise-to-music mappings into the database.

    Args:
        mappings: List of dicts with keys matching the mapping table columns
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.executemany(
            """
            INSERT OR REPLACE INTO exercise_music_mapping 
            (exercise_id, music_ref, recommendation, specific_comment) 
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    m["exercise_id"],
                    m["music_ref"],
                    m["recommendation"],
                    m["specific_comment"],
                )
                for m in mappings
            ],
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error inserting exercise-music mappings: {e}")
    finally:
        conn.close()


# Query functions for retrieving data


def get_all_exercise_categories():
    """Get all exercise categories."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM exercise_categories ORDER BY category_name")
        return cursor.fetchall()
    finally:
        conn.close()


def get_exercises_by_category(category):
    """Get exercises by category."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM exercises WHERE category = ? ORDER BY id", (category,)
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_exercises_by_phase(phase):
    """Get exercises by phase."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM exercises WHERE phase = ? ORDER BY id", (phase,))
        return cursor.fetchall()
    finally:
        conn.close()


def get_all_exercises():
    """Get all exercises."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM exercises ORDER BY phase, id")
        return cursor.fetchall()
    finally:
        conn.close()


def get_music_for_exercise(exercise_id):
    """Get all music associated with a specific exercise."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT m.*, em.recommendation, em.specific_comment
            FROM musics m
            JOIN exercise_music_mapping em ON m.music_ref = em.music_ref
            WHERE em.exercise_id = ?
            ORDER BY em.recommendation DESC
            """,
            (exercise_id,),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_music_by_ref(music_ref):
    """Get music by reference ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM musics WHERE music_ref = ?", (music_ref,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_songs_for_exercise(exercise_id):
    """
    Get all songs associated with a specific exercise with detailed metadata.

    Args:
        exercise_id: The ID of the exercise

    Returns:
        List of song dictionaries with metadata
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT 
                m.music_ref, m.title, m.artist, m.bpm, m.duration, m.filename,
                m.collection_cd, em.recommendation, em.specific_comment
            FROM musics m
            JOIN exercise_music_mapping em ON m.music_ref = em.music_ref
            WHERE em.exercise_id = ?
            ORDER BY em.recommendation DESC, m.title
            """,
            (exercise_id,),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_exercises_by_song_name(song_name):
    """
    Get exercises that are associated with songs matching the given name or vivencia.

    Args:
        song_name: The song name or vivencia line to search for

    Returns:
        List of exercises associated with matching songs
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Clean the input and ensure case-insensitive search
        search_term = song_name.strip()

        # Use LIKE with wildcards for partial matching on both title and artist
        # SQLite's LIKE is case-insensitive by default
        cursor.execute(
            """
            SELECT DISTINCT e.*
            FROM exercises e
            JOIN exercise_music_mapping em ON e.id = em.exercise_id
            JOIN musics m ON em.music_ref = m.music_ref
            WHERE m.title LIKE ? OR m.artist LIKE ? OR m.collection_cd LIKE ?
            ORDER BY e.phase, e.category, e.name
            """,
            (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_all_songs():
    """Get all songs in the catalogue with metadata."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT music_ref, title, artist, bpm, duration, filename, collection_cd
            FROM musics
            ORDER BY title
            """
        )
        return cursor.fetchall()
    finally:
        conn.close()


# Session management functions


def save_session(session_data, session_exercises):
    """
    Save or update a session with its exercises.

    Args:
        session_data: Dict with session metadata (id, name, description, date, tags)
        session_exercises: List of tuples (exercise_name, music_ref, exercise_id) in sequence

    Returns:
        Tuple of (success, message, session_id)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        conn.execute("BEGIN TRANSACTION")

        # Check if this is an update to an existing session
        is_update = "id" in session_data and session_data["id"]
        current_version = 1

        if is_update:
            # Check for version conflicts
            cursor.execute(
                "SELECT version FROM sessions WHERE id = ?", (session_data["id"],)
            )
            result = cursor.fetchone()

            if result:
                current_version = result["version"] + 1

                # If conflict detection is required, check versions
                if (
                    session_data.get("version")
                    and session_data["version"] < current_version - 1
                ):
                    conn.rollback()
                    return (
                        False,
                        "Session was modified elsewhere. Please reload before saving.",
                        session_data["id"],
                    )
            else:
                # ID provided but session doesn't exist
                is_update = False

        # Prepare timestamps
        now = (
            session_data.get("updated_at")
            or session_data.get("created_at")
            or session_data.get("timestamp")
            or datetime.now().isoformat()
        )

        if not is_update:
            # Generate a new UUID if not provided or not an update
            session_id = session_data.get("id") or str(uuid.uuid4())

            cursor.execute(
                """
                INSERT INTO sessions
                (id, name, description, date, tags, created_at, updated_at, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    session_data["name"],
                    session_data.get("description", ""),
                    session_data.get("date", ""),
                    session_data.get("tags", ""),
                    now,
                    now,
                    1,
                ),
            )
        else:
            session_id = session_data["id"]

            cursor.execute(
                """
                UPDATE sessions
                SET name = ?, description = ?, date = ?, tags = ?, 
                    updated_at = ?, version = ?
                WHERE id = ?
                """,
                (
                    session_data["name"],
                    session_data.get("description", ""),
                    session_data.get("date", ""),
                    session_data.get("tags", ""),
                    now,
                    current_version,
                    session_id,
                ),
            )

            # Delete existing session exercises to replace with new ones
            cursor.execute(
                "DELETE FROM session_exercises WHERE session_id = ?", (session_id,)
            )

        # Insert the session exercises
        for i, exercise_tuple in enumerate(session_exercises):
            # Handle different tuple lengths (2, 3, or 4 elements)
            if len(exercise_tuple) >= 4:
                exercise_name, music_ref, exercise_id, notes = exercise_tuple
            elif len(exercise_tuple) == 3:
                exercise_name, music_ref, exercise_id = exercise_tuple
                notes = ""  # Default empty notes
            else:
                exercise_name, music_ref = exercise_tuple
                notes = ""  # Default empty notes
                # Extract exercise ID from the exercise_name format "Name [id ID]"
                exercise_id = None
                if "[id " in exercise_name:
                    exercise_id = exercise_name.split("[id ")[1].split("]")[0].strip()

            cursor.execute(
                """
                INSERT INTO session_exercises
                (session_id, sequence_number, exercise_id, music_ref, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, i + 1, exercise_id, music_ref, notes),
            )

        conn.commit()
        return True, "Session saved successfully", session_id

    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Error saving session: {e}", None
    finally:
        conn.close()


def get_session_by_id(session_id):
    """
    Get session details by ID.

    Args:
        session_id: The UUID of the session

    Returns:
        Tuple of (session_data, session_exercises)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get session metadata
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        session_data = cursor.fetchone()

        if not session_data:
            return None, []

        # Get session exercises
        cursor.execute(
            """
            SELECT se.*, e.name, e.id as exercise_original_id
            FROM session_exercises se
            LEFT JOIN exercises e ON se.exercise_id = e.id
            WHERE se.session_id = ?
            ORDER BY se.sequence_number
            """,
            (session_id,),
        )
        exercises = cursor.fetchall()

        # Format exercises as expected by the UI
        session_exercises = []
        for ex in exercises:
            exercise_name = (
                f"{ex['name']} [id {ex['exercise_original_id']}]"
                if ex["name"]
                else "Unknown Exercise"
            )
            # Create tuple with four elements: exercise name, music ref, exercise ID, and notes
            # Check if the notes column exists and has a value
            # try:
            #     notes = ex["notes"] if ex["notes"] is not None else ""
            # except (IndexError, KeyError):
            #     notes = ""

            session_exercises.append(
                (
                    exercise_name,
                    ex["music_ref"],
                    ex["exercise_id"],  # Store the exercise ID for song retrieval
                    ex["notes"] if ex["notes"] is not None else "",  # Include notes
                )
            )

        return dict(session_data), session_exercises

    except sqlite3.Error as e:
        print(f"Error retrieving session: {e}")
        return None, []
    finally:
        conn.close()


def get_all_sessions():
    """
    Get a list of all saved sessions.

    Returns:
        List of session metadata dicts
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, name, date, updated_at, 
                   (SELECT COUNT(*) FROM session_exercises WHERE session_id = sessions.id) as exercise_count
            FROM sessions
            ORDER BY updated_at DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error retrieving sessions: {e}")
        return []
    finally:
        conn.close()


def delete_session(session_id):
    """
    Delete a session and its exercises.

    Args:
        session_id: The UUID of the session to delete

    Returns:
        Boolean success
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        conn.execute("BEGIN TRANSACTION")

        # Delete session exercises first (could use cascade, but being explicit)
        cursor.execute(
            "DELETE FROM session_exercises WHERE session_id = ?", (session_id,)
        )

        # Delete the session
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

        conn.commit()
        return True
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error deleting session: {e}")
        return False
    finally:
        conn.close()
