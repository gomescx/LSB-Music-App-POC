"""
Migration script to add a 'cimeb' column to the exercises table.
This column indicates whether the exercise is from Cimeb or from other facilitators.
"""

import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "lsb_catalogue.db"


def add_cimeb_column():
    """Add cimeb column to exercises table if it doesn't exist."""
    
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return False
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if cimeb column already exists
        cursor.execute("PRAGMA table_info(exercises)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'cimeb' in columns:
            print("The 'cimeb' column already exists in the exercises table.")
            return True
        
        # Add the cimeb column with default value True (assuming existing exercises are Cimeb)
        cursor.execute("ALTER TABLE exercises ADD COLUMN cimeb BOOLEAN DEFAULT 1")
        
        print("Successfully added 'cimeb' column to exercises table.")
        print("All existing exercises are marked as Cimeb (cimeb=1) by default.")
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def verify_column_addition():
    """Verify that the cimeb column was added successfully."""
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check table schema
        cursor.execute("PRAGMA table_info(exercises)")
        schema = cursor.fetchall()
        
        print("\nUpdated exercises table schema:")
        for column in schema:
            print(f"  {column}")
        
        # Check a sample of data
        cursor.execute("SELECT id, name, cimeb FROM exercises LIMIT 5")
        sample_data = cursor.fetchall()
        
        print("\nSample exercises with cimeb column:")
        for row in sample_data:
            print(f"  ID: {row[0]}, Name: {row[1]}, Cimeb: {row[2]}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"Database error during verification: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during verification: {e}")
        return False
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print("Adding 'cimeb' column to exercises table...")
    
    if add_cimeb_column():
        verify_column_addition()
        print("\nMigration completed successfully!")
    else:
        print("\nMigration failed!")
