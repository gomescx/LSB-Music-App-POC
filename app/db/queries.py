"""
Database query functions for the LSB Music App.
"""

import sqlite3
from .schema import get_db_connection

def insert_exercise_categories(categories):
    """Insert exercise categories into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.executemany(
            "INSERT OR REPLACE INTO exercise_categories (category_name) VALUES (?)",
            [(category,) for category in categories]
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
            [(ex['id'], ex['phase'], ex['category'], ex['name'], 
              ex['short_name'], ex['aka'], ex['phase_reviewer']) 
             for ex in exercises]
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
            [(m['music_ref'], m['collection_cd'], m['filename'], m['title'],
              m['artist'], m['duration'], m['v'], m['c'], m['a'], 
              m['s'], m['t'], m['bpm']) 
             for m in musics]
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
            [(m['exercise_id'], m['music_ref'], m['recommendation'], 
              m['specific_comment']) 
             for m in mappings]
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
            "SELECT * FROM exercises WHERE category = ? ORDER BY id",
            (category,)
        )
        return cursor.fetchall()
    finally:
        conn.close()

def get_exercises_by_phase(phase):
    """Get exercises by phase."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM exercises WHERE phase = ? ORDER BY id",
            (phase,)
        )
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
            (exercise_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()

def get_music_by_ref(music_ref):
    """Get music by reference ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM musics WHERE music_ref = ?",
            (music_ref,)
        )
        return cursor.fetchone()
    finally:
        conn.close()
