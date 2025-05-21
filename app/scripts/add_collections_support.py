"""
Migration script to add collections support to the SQLite database.
Run this script after activating your .venv.
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "lsb_catalogue.db"

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def main():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create collections table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            collection_code TEXT PRIMARY KEY,
            description TEXT
        );
    ''')

    # 2. Insert initial LSB record
    cursor.execute('''
        INSERT OR IGNORE INTO collections (collection_code, description)
        VALUES ('LSB', 'London School of Biodanza');
    ''')

    # 3. Add collection_code to musics if not exists
    if not column_exists(cursor, 'musics', 'collection_code'):
        cursor.execute('''
            ALTER TABLE musics ADD COLUMN collection_code TEXT;
        ''')
    # 4. Populate musics.collection_code with 'LSB'
    cursor.execute('''
        UPDATE musics SET collection_code = 'LSB' WHERE collection_code IS NULL;
    ''')

    # 5. Add collection_code to exercise_music_mapping if not exists
    if not column_exists(cursor, 'exercise_music_mapping', 'collection_code'):
        cursor.execute('''
            ALTER TABLE exercise_music_mapping ADD COLUMN collection_code TEXT;
        ''')
    # 6. Populate exercise_music_mapping.collection_code with 'LSB'
    cursor.execute('''
        UPDATE exercise_music_mapping SET collection_code = 'LSB' WHERE collection_code IS NULL;
    ''')

    conn.commit()
    cursor.close()
    conn.close()
    print('Migration completed successfully.')

if __name__ == '__main__':
    main()
