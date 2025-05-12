"""
Script to test session management functionality.
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime

# Make sure the app directory is in the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.db.queries import (
    save_session,
    get_session_by_id,
    get_all_sessions,
    delete_session,
)


def test_save_session():
    """Test saving a session."""
    print("\n--- Testing Save Session ---")

    # Create test data
    session_data = {
        "id": str(uuid.uuid4()),
        "name": "Test Session 1",
        "description": "This is a test session",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "tags": "#test #example",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    session_exercises = [
        ("Exercise 1 [id 1]", "music_ref_1"),
        ("Exercise 2 [id 2]", None),
        ("Exercise 3 [id 3]", "music_ref_3"),
    ]

    # Save the session
    success, message, session_id = save_session(session_data, session_exercises)

    print(f"Save session result: {success}")
    print(f"Message: {message}")
    print(f"Session ID: {session_id}")

    return session_id if success else None


def test_get_session(session_id):
    """Test retrieving a session."""
    print("\n--- Testing Get Session ---")

    # Retrieve the session
    session_data, session_exercises = get_session_by_id(session_id)

    if not session_data:
        print(f"Failed to retrieve session with ID {session_id}")
        return False

    print(f"Retrieved session data: {session_data}")
    print(f"Retrieved session exercises: {session_exercises}")

    return True


def test_list_sessions():
    """Test listing all sessions."""
    print("\n--- Testing List Sessions ---")

    # Get all sessions
    sessions = get_all_sessions()

    print(f"Found {len(sessions)} sessions:")
    for session in sessions:
        print(f"  - {session['name']} (ID: {session['id']}, Date: {session['date']})")

    return True


def test_update_session(session_id):
    """Test updating a session."""
    print("\n--- Testing Update Session ---")

    # Get the current session
    session_data, session_exercises = get_session_by_id(session_id)

    if not session_data:
        print(f"Failed to retrieve session with ID {session_id}")
        return False

    # Update the session data
    session_data["name"] = "Updated Test Session"
    session_data["description"] = "This is an updated test session"
    session_data["updated_at"] = datetime.now().isoformat()

    # Update the exercises
    session_exercises.append(("Exercise 4 [id 4]", None))

    # Save the updated session
    success, message, updated_id = save_session(session_data, session_exercises)

    print(f"Update session result: {success}")
    print(f"Message: {message}")

    return success


def test_delete_session(session_id):
    """Test deleting a session."""
    print("\n--- Testing Delete Session ---")

    # Delete the session
    success = delete_session(session_id)

    print(f"Delete session result: {success}")

    return success


def main():
    """Run all tests."""
    print("Running session management tests...")

    # Test saving a session
    session_id = test_save_session()
    if not session_id:
        print("Failed to save session, cannot continue tests.")
        return

    # Test retrieving a session
    if not test_get_session(session_id):
        print("Failed to retrieve session, cannot continue tests.")
        return

    # Test listing all sessions
    test_list_sessions()

    # Test updating a session
    if not test_update_session(session_id):
        print("Failed to update session, cannot continue tests.")
        return

    # Get the updated session to verify changes
    test_get_session(session_id)

    # Test listing all sessions after update
    test_list_sessions()

    # Uncomment to test deleting sessions
    # test_delete_session(session_id)
    # test_list_sessions()

    print("\nAll tests completed!")


if __name__ == "__main__":
    main()
