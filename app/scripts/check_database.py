import os
import sys
import sqlite3
from pathlib import Path

# Make sure the app directory is in the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def check_database():
    """Check the contents of the database to verify it was loaded correctly."""
    db_path = project_root / "data" / "lsb_catalogue.db"
    
    if not db_path.exists():
        print(f"Error: Database file not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    
    try:
        # Check the number of records in each table
        tables = ['exercise_categories', 'exercises', 'musics', 'exercise_music_mapping']
        
        print("\nDatabase Contents Summary:")
        print("=========================")
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            print(f"{table}: {count} records")
        
        # Sample from each table
        print("\nSample Data:")
        print("===========")
        
        # Exercise Categories
        print("\nExercise Categories (first 5):")
        cursor.execute("SELECT * FROM exercise_categories LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  - {row['category_name']}")
        
        # Exercises
        print("\nExercises (first 5):")
        cursor.execute("SELECT * FROM exercises LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  - ID: {row['id']}, Name: {row['name']}, Phase: {row['phase']}, Category: {row['category']}")
        
        # Musics
        print("\nMusics (first 5):")
        cursor.execute("SELECT * FROM musics LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  - Ref: {row['music_ref']}, Title: {row['title']}, Artist: {row['artist']}")
        
        # Exercise-Music Mappings
        print("\nExercise-Music Mappings (first 5):")
        cursor.execute("SELECT * FROM exercise_music_mapping LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  - Exercise: {row['exercise_id']}, Music: {row['music_ref']}, Recommendation: {row['recommendation']}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()
