"""
Database initialization module for the LSB Music App.
"""

from .schema import init_db, get_db_connection
from .queries import (
    insert_exercise_categories, insert_exercises, insert_musics, 
    insert_exercise_music_mappings,
    get_all_exercise_categories, get_exercises_by_category,
    get_exercises_by_phase, get_all_exercises,
    get_music_for_exercise, get_music_by_ref
)

__all__ = [
    'init_db', 'get_db_connection',
    'insert_exercise_categories', 'insert_exercises', 'insert_musics', 'insert_exercise_music_mappings',
    'get_all_exercise_categories', 'get_exercises_by_category',
    'get_exercises_by_phase', 'get_all_exercises',
    'get_music_for_exercise', 'get_music_by_ref'
]
