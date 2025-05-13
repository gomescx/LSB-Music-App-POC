#!/usr/bin/env python3
"""
Script to reload just the musics table after schema changes.
"""

import sys
import pandas as pd
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.schema import get_db_connection
from app.data_loader import load_lsb_catalogue


def reset_musics_table():
    """Drop and recreate the musics table with the new schema."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("Deleting all records from the musics table...")
        cursor.execute("DELETE FROM musics")

        # Check if we need to update the schema
        cursor.execute("PRAGMA table_info(musics)")
        columns = cursor.fetchall()
        needs_update = False

        for col in columns:
            # Check if v,c,a,s,t are TEXT type
            if col[1] in ("v", "c", "a", "s", "t") and col[2] != "TEXT":
                needs_update = True
                break

        if needs_update:
            print("Updating musics table schema...")
            # Create a temporary table with the new schema
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS musics_new (
                music_ref TEXT PRIMARY KEY,
                collection_cd TEXT,
                filename TEXT,
                title TEXT,
                artist TEXT,
                duration TEXT,
                v TEXT,
                c TEXT,
                a TEXT,
                s TEXT,
                t TEXT,
                bpm INTEGER
            )
            """
            )

            # Drop the old table and rename the new one
            cursor.execute("DROP TABLE musics")
            cursor.execute("ALTER TABLE musics_new RENAME TO musics")

        conn.commit()
        print("Musics table reset successfully.")
        return True

    except Exception as e:
        conn.rollback()
        print(f"Error resetting musics table: {e}")
        return False

    finally:
        conn.close()


def reload_musics_data():
    """Reload just the musics data from the Excel file."""
    from app.db.queries import insert_musics

    excel_path = (
        Path(__file__).resolve().parent.parent / "input" / "LSB_Base_flatfile.xlsx"
    )

    if not excel_path.exists():
        print(f"Error: Excel file not found at {excel_path}")
        return False

    try:
        # Load only the Musics sheet from Excel
        excel_file = pd.ExcelFile(excel_path)
        musics_df = pd.read_excel(excel_file, sheet_name="Musics")

        # Process music entries
        musics = []
        for _, row in musics_df.iterrows():
            try:
                # Convert time to string format
                duration = str(row["Time"]) if not pd.isna(row["Time"]) else None

                # Helper function to safely convert to int
                def safe_int(value):
                    if pd.isna(value):
                        return None
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return None

                # Helper function to safely get text value
                def safe_text(value):
                    if pd.isna(value):
                        return None
                    return str(value)

                music = {
                    "music_ref": str(row["MusicRef"]),
                    "collection_cd": (
                        str(row["Music 'CD' (Genre tag)"])
                        if not pd.isna(row["Music 'CD' (Genre tag)"])
                        else None
                    ),
                    "filename": (
                        str(row["Music filename"])
                        if not pd.isna(row["Music filename"])
                        else None
                    ),
                    "title": (
                        str(row["Music Title (Movement Name tag)"])
                        if not pd.isna(row["Music Title (Movement Name tag)"])
                        else None
                    ),
                    "artist": (
                        str(row["Music Artist (Artist tag)"])
                        if not pd.isna(row["Music Artist (Artist tag)"])
                        else None
                    ),
                    "duration": duration,
                    # Handle V,C,A,S,T as text values
                    "v": safe_text(row["V"]),
                    "c": safe_text(row["C"]),
                    "a": safe_text(row["A"]),
                    "s": safe_text(row["S"]),
                    "t": safe_text(row["T"]),
                    "bpm": safe_int(row["BPM"]),
                }
                musics.append(music)
            except Exception as e:
                print(f"Warning: Error processing music {row['MusicRef']}: {e}")
                continue

        # Insert musics into the database
        insert_musics(musics)
        print(f"Successfully loaded {len(musics)} music entries")
        return True

    except Exception as e:
        print(f"Error loading musics: {e}")
        return False


if __name__ == "__main__":
    if reset_musics_table():
        reload_musics_data()
