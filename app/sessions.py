"""
Session management functionality for the LSB Music App.
"""

import streamlit as st
import uuid
from datetime import datetime
import time
from typing import Dict, List, Tuple, Optional
import threading

from app.db.queries import (
    save_session,
    get_session_by_id,
    get_all_sessions,
    delete_session,
)


# Global auto-save timer
_autosave_timer = None
_autosave_interval = 30  # seconds


def initialize_session_metadata():
    """Initialize session metadata state if it doesn't exist."""
    if "session_metadata" not in st.session_state:
        st.session_state.session_metadata = {
            "id": None,
            "name": "",
            "description": "",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "tags": "",
            "version": 1,
            "created_at": None,
            "updated_at": None,
            "last_saved": None,
            "has_unsaved_changes": False,
        }

    # Initialize confirmation flags
    if "confirming_load" not in st.session_state:
        st.session_state.confirming_load = False

    if "confirming_delete" not in st.session_state:
        st.session_state.confirming_delete = False


def sanitize_input(input_text: str) -> str:
    """
    Basic sanitization of user input to prevent injection.

    Args:
        input_text: Text to sanitize

    Returns:
        Sanitized text
    """
    if not input_text:
        return ""

    # Simple sanitization - remove dangerous SQL characters
    dangerous_chars = ["'", '"', ";", "--", "/*", "*/"]
    result = input_text
    for char in dangerous_chars:
        result = result.replace(char, "")

    return result


def save_current_session(show_message: bool = True) -> Tuple[bool, str, Optional[str]]:
    """
    Save the current session to the database.

    Args:
        show_message: Whether to show a success/error message

    Returns:
        Tuple of (success, message, session_id)
    """
    # Validate required fields
    if not st.session_state.session_metadata.get("name"):
        if show_message:
            st.error("Session name is required")
        return False, "Session name is required", None

    # Sanitize inputs
    session_data = {
        "id": st.session_state.session_metadata.get("id"),
        "name": sanitize_input(st.session_state.session_metadata.get("name", "")),
        "description": sanitize_input(
            st.session_state.session_metadata.get("description", "")
        ),
        "date": sanitize_input(st.session_state.session_metadata.get("date", "")),
        "tags": sanitize_input(st.session_state.session_metadata.get("tags", "")),
        "version": st.session_state.session_metadata.get("version", 1),
        "timestamp": datetime.now().isoformat(),
    }

    # Save to database
    success, message, session_id = save_session(
        session_data, st.session_state.session_exercises
    )

    if success:
        # Update session state
        st.session_state.session_metadata["id"] = session_id
        st.session_state.session_metadata["version"] += 1
        st.session_state.session_metadata["updated_at"] = datetime.now().isoformat()
        st.session_state.session_metadata["last_saved"] = datetime.now().isoformat()
        st.session_state.session_metadata["has_unsaved_changes"] = False

        if show_message:
            st.success(message)
    else:
        if show_message:
            st.error(message)

    return success, message, session_id


def load_session(session_id: str) -> bool:
    """
    Load a session from the database.

    Args:
        session_id: The UUID of the session to load

    Returns:
        Boolean success
    """
    session_data, session_exercises = get_session_by_id(session_id)

    if not session_data:
        st.error(f"Failed to load session: Session not found")
        return False

    # Update session state
    st.session_state.session_metadata = {
        "id": session_data["id"],
        "name": session_data["name"],
        "description": session_data["description"],
        "date": session_data["date"],
        "tags": session_data["tags"],
        "version": session_data["version"],
        "created_at": session_data["created_at"],
        "updated_at": session_data["updated_at"],
        "last_saved": datetime.now().isoformat(),
        "has_unsaved_changes": False,
    }

    # Update session exercises
    st.session_state.session_exercises = session_exercises

    return True


def mark_session_changed():
    """Mark the current session as having unsaved changes."""
    if "session_metadata" in st.session_state:
        st.session_state.session_metadata["has_unsaved_changes"] = True


def setup_autosave():
    """Setup autosave functionality."""
    global _autosave_timer

    # Cancel existing timer if any
    if _autosave_timer:
        _autosave_timer.cancel()

    # Define autosave function
    def autosave_function():
        global _autosave_timer

        # Check if there are unsaved changes
        if (
            st.session_state.get("session_metadata")
            and st.session_state.session_metadata.get("has_unsaved_changes", False)
            and st.session_state.session_metadata.get("name")
        ):

            # Try to save without showing messages
            save_current_session(show_message=False)

        # Schedule next autosave
        _autosave_timer = threading.Timer(_autosave_interval, autosave_function)
        _autosave_timer.daemon = True
        _autosave_timer.start()

    # Start the autosave timer
    _autosave_timer = threading.Timer(_autosave_interval, autosave_function)
    _autosave_timer.daemon = True
    _autosave_timer.start()


def render_session_metadata_ui():
    """
    Render the session metadata UI component.

    Returns:
        Boolean indicating if the session was saved
    """
    st.subheader("Session Metadata")

    # Session ID display (if exists)
    if st.session_state.session_metadata.get("id"):
        session_id = st.session_state.session_metadata["id"]
        st.text(f"Session ID: {session_id}")

    # Last saved indicator
    if st.session_state.session_metadata.get("last_saved"):
        last_saved = datetime.fromisoformat(
            st.session_state.session_metadata["last_saved"]
        )
        st.text(f"Last saved: {last_saved.strftime('%H:%M:%S')}")

    # Unsaved changes indicator
    if st.session_state.session_metadata.get("has_unsaved_changes", False):
        st.warning("⚠️ Unsaved changes")

    # Session name field
    name = st.text_input(
        "Session Name*",
        value=st.session_state.session_metadata.get("name", ""),
        key="session_name_input",
    )
    if name != st.session_state.session_metadata.get("name", ""):
        st.session_state.session_metadata["name"] = name
        mark_session_changed()

    # Date field with default to today
    date_val = st.session_state.session_metadata.get(
        "date", datetime.now().strftime("%Y-%m-%d")
    )
    date = st.date_input(
        "Session Date",
        value=datetime.strptime(date_val, "%Y-%m-%d") if date_val else datetime.now(),
        key="session_date_input",
    )
    new_date = date.strftime("%Y-%m-%d")
    if new_date != st.session_state.session_metadata.get("date", ""):
        st.session_state.session_metadata["date"] = new_date
        mark_session_changed()

    # Description field
    description = st.text_area(
        "Description",
        value=st.session_state.session_metadata.get("description", ""),
        key="session_description_input",
    )
    if description != st.session_state.session_metadata.get("description", ""):
        st.session_state.session_metadata["description"] = description
        mark_session_changed()

    # Tags field
    tags = st.text_input(
        "Tags",
        value=st.session_state.session_metadata.get("tags", ""),
        help="Enter tags in #tag format, separated by spaces",
        key="session_tags_input",
    )
    if tags != st.session_state.session_metadata.get("tags", ""):
        st.session_state.session_metadata["tags"] = tags
        mark_session_changed()

    # Save button
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Save Session", key="save_session_button"):
            success, _, _ = save_current_session(show_message=True)
            return success

    # Only show clear button if we have an existing session
    with col2:
        if st.session_state.session_metadata.get("id"):
            if st.button("Clear Form", key="clear_session_button"):
                st.session_state.session_metadata = {
                    "id": None,
                    "name": "",
                    "description": "",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "tags": "",
                    "version": 1,
                    "created_at": None,
                    "updated_at": None,
                    "last_saved": None,
                    "has_unsaved_changes": False,
                }
                return False

    return False


def render_session_list_ui():
    """
    Render the session list UI component for loading saved sessions.

    Returns:
        Boolean indicating if a session was loaded
    """
    st.subheader("Saved Sessions")

    # Get all sessions
    sessions = get_all_sessions()

    if not sessions:
        st.info("No saved sessions found")
        return False

    # Create a selectbox with session names
    session_options = {
        f"{s['name']} ({s['date']})" if s["date"] else s["name"]: s["id"]
        for s in sessions
    }
    selected_session_name = st.selectbox(
        "Select a session to load",
        options=list(session_options.keys()),
        key="session_select",
    )

    if selected_session_name:
        selected_session_id = session_options[selected_session_name]

        # Check if we're in confirmation mode
        if st.session_state.get("confirming_load", False):
            st.warning(
                "You have unsaved changes. Do you want to proceed and lose those changes?"
            )

            # Show confirm and cancel buttons side by side
            confirm_col1, confirm_col2 = st.columns([1, 1])
            with confirm_col1:
                if st.button("Confirm Load", key="confirm_load_button"):
                    # Reset confirmation flag
                    st.session_state.confirming_load = False

                    # Load the selected session
                    success = load_session(selected_session_id)
                    if success:
                        st.success(
                            f"Session '{selected_session_name}' loaded successfully"
                        )
                        return True

            with confirm_col2:
                if st.button("Cancel", key="cancel_load_button"):
                    # Reset confirmation flag
                    st.session_state.confirming_load = False
                    return False

        else:
            # Show regular load and delete buttons side by side
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Load Session", key="load_session_button"):
                    # Check for unsaved changes
                    if st.session_state.session_metadata.get(
                        "has_unsaved_changes", False
                    ):
                        # Set confirmation mode
                        st.session_state.confirming_load = True
                        return False

                    # No unsaved changes, proceed with loading
                    success = load_session(selected_session_id)
                    if success:
                        st.success(
                            f"Session '{selected_session_name}' loaded successfully"
                        )
                        return True

        with col2:
            # Only show delete button if not in confirmation mode for loading
            if not st.session_state.get("confirming_load", False):
                if st.button("Delete Session", key="delete_session_button"):
                    # Set confirmation mode
                    st.session_state.confirming_delete = True
                    return False

        # Handle delete confirmation if needed
        if st.session_state.get("confirming_delete", False):
            st.warning(
                f"Are you sure you want to delete session '{selected_session_name}'?"
            )

            # Show confirm and cancel buttons side by side
            confirm_col1, confirm_col2 = st.columns([1, 1])
            with confirm_col1:
                if st.button("Confirm Delete", key="confirm_delete_button"):
                    # Reset confirmation flag
                    st.session_state.confirming_delete = False

                    # Delete the session
                    success = delete_session(selected_session_id)
                    if success:
                        st.success(
                            f"Session '{selected_session_name}' deleted successfully"
                        )
                        return True

            with confirm_col2:
                if st.button("Cancel", key="cancel_delete_button"):
                    # Reset confirmation flag
                    st.session_state.confirming_delete = False
                    return False

    return False
