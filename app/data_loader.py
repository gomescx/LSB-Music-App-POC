"""
Module for loading LSB Excel data into the SQLite database.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from app.db.schema import init_db
from app.db.queries import (
    insert_exercise_categories,
    insert_exercises,
    insert_musics,
    insert_exercise_music_mappings,
)


def load_lsb_catalogue(excel_path):
    """
    Load LSB catalogue data from Excel file into the SQLite database.

    Args:
        excel_path (str): Path to the LSB Excel file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Initialize the database
        if not init_db():
            return False

        # Load the Excel file
        excel_file = pd.ExcelFile(excel_path)

        # Load Exercise Categories
        categories_df = pd.read_excel(excel_file, sheet_name="Exercise-Category")
        categories = categories_df["IBFexCATEGORY"].tolist()
        insert_exercise_categories(categories)

        # Load Exercises
        exercises_df = pd.read_excel(excel_file, sheet_name="Exercises")
        exercises = []
        for _, row in exercises_df.iterrows():
            try:
                # Keep the IBFex as string to handle values like "14a"
                exercise_id = str(row["IBFex"]).strip()

                if not exercise_id:  # Skip empty IDs
                    print(f"Warning: Skipping exercise with empty ID")
                    continue

                exercise = {
                    "id": exercise_id,
                    "phase": float(row["Phase"]) if not pd.isna(row["Phase"]) else None,
                    "category": str(row["IBFexCATEGORY"]),
                    "name": str(row["IBFexNAME"]),
                    "short_name": (
                        str(row["IBFexSHORT FORM NAME"])
                        if not pd.isna(row["IBFexSHORT FORM NAME"])
                        else None
                    ),
                    "aka": str(row["AKA"]) if not pd.isna(row["AKA"]) else None,
                    "phase_reviewer": (
                        str(row["Phase_reviewer"])
                        if not pd.isna(row["Phase_reviewer"])
                        else None
                    ),
                }
                exercises.append(exercise)
            except Exception as e:
                print(f"Warning: Error processing exercise {row['IBFex']}: {e}")
        insert_exercises(exercises)

        # Load Musics
        musics_df = pd.read_excel(excel_file, sheet_name="Musics")
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
            except Exception as e:
                print(f"Warning: Error processing music {row['MusicRef']}: {e}")
                continue
            musics.append(music)
        insert_musics(musics)

        # Load Exercise-to-Music mappings
        mappings_df = pd.read_excel(excel_file, sheet_name="Exercises-to-Musics")
        mappings = []
        for _, row in mappings_df.iterrows():
            try:
                # Keep the IBFex as string to handle values like "14a"
                exercise_id = str(row["IBFex"]).strip()

                if not exercise_id:  # Skip empty IDs
                    print(f"Warning: Skipping mapping with empty exercise ID")
                    continue

                mapping = {
                    "exercise_id": exercise_id,
                    "music_ref": str(row["MusicRef"]),
                    "recommendation": (
                        str(row["Recommendation"])
                        if not pd.isna(row["Recommendation"])
                        else None
                    ),
                    "specific_comment": (
                        str(row["Exercise-Music specific comment"])
                        if not pd.isna(row["Exercise-Music specific comment"])
                        else None
                    ),
                }
                mappings.append(mapping)
            except Exception as e:
                print(
                    f"Warning: Error processing mapping for exercise {row['IBFex']} and music {row['MusicRef']}: {e}"
                )
        insert_exercise_music_mappings(mappings)

        return True

    except Exception as e:
        print(f"Error loading LSB catalogue: {e}")
        return False


if __name__ == "__main__":
    # Path to the Excel file
    excel_path = Path(__file__).parent.parent / "input" / "LSB_Base_flatfile.xlsx"

    if load_lsb_catalogue(excel_path):
        print("LSB catalogue loaded successfully!")
    else:
        print("Failed to load LSB catalogue.")
