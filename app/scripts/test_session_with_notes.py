#!/usr/bin/env python3
"""
Test script to create a session with notes to verify that notes are saved and loaded correctly.
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.db.queries import (
    save_session,
    get_session_by_id,
)


def create_test_session_with_notes():
    """
    Create a test session with notes for each exercise.
    """
    print("Creating a test session with notes...")

    # Create test data
    session_data = {
        "id": str(uuid.uuid4()),
        "name": "Test Session With Notes",
        "description": "This session was created to test notes functionality",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "tags": "#test #notes",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    # Create session exercises with notes
    session_exercises = [
        (
            "CIRCLE OF INITIATION [id 1]",
            "xBA73-16",
            "1",
            "This is a note for exercise 1.",
        ),
        (
            "SINUOUS CIRCLE [id 2]",
            "xBA34-13",
            "2",
            "Some consigna instructions for exercise 2.",
        ),
        ("JOYOUS CIRCLE [id 4]", "IBF03-14", "4", "Personal cues: remember to smile!"),
        (
            "ABDOMINAL BREATHING [id 68]",
            "DBO01-30",
            "68",
            "Observation: slow tempo works better for beginners.",
        ),
    ]

    # Save the session
    success, message, session_id = save_session(session_data, session_exercises)

    if success:
        print(f"Test session created successfully with ID: {session_id}")

        # Verify by loading and checking the notes
        session_data, session_exercises = get_session_by_id(session_id)

        print("\nVerifying loaded session data:")
        for i, exercise in enumerate(session_exercises):
            if len(exercise) >= 4:
                print(f"Exercise {i+1}: {exercise[0]}")
                print(f"  Notes: {repr(exercise[3])}")
            else:
                print(f"Exercise {i+1}: {exercise[0]}")
                print(f"  WARNING: No notes found in tuple: {exercise}")

        return session_id
    else:
        print(f"Failed to create test session: {message}")
        return None


if __name__ == "__main__":
    session_id = create_test_session_with_notes()
    if session_id:
        print(f"\nSession created with ID: {session_id}")
        print("You can load this session in the app to verify notes functionality.")
    else:
        print("\nFailed to create test session.")
        sys.exit(1)
