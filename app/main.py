"""
LSB Music App - Main Streamlit App
"""

from pathlib import Path
import streamlit as st
import sys

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.ui import initialize_session_state
from app.ui import exercise_selector, exercise_list
from app.sessions import (
    render_session_metadata_ui,
    render_session_list_ui,
    mark_session_changed,
    save_current_session,
)


def main():
    """Main function to run the Streamlit app."""
    # Set page title and icon
    st.set_page_config(page_title="LSB Music App", page_icon="🎵", layout="wide")

    # Initialize session state
    initialize_session_state()

    # Ensure show_exercise_selector is always initialized
    if "show_exercise_selector" not in st.session_state:
        st.session_state.show_exercise_selector = True

    # App header
    st.title("LSB Music App")
    st.subheader("Build and Manage Biodanza Sessions")

    # Sidebar for filtering and controls
    with st.sidebar:
        st.header("Exercise Filters")

        # Phase selector
        phase_options = ["All", "1", "2", "3", "4", "5"]
        selected_phase = st.radio(
            "Select Phase:",
            options=phase_options,
            help="Filter exercises by phase (1-5) or show all",
        )

        # Name filter
        name_filter = st.text_input(
            "Filter by name:",
            help="Type part of an exercise name to filter the list",
            key="name_filter",
        )

        # Song filter (new feature)
        st.markdown("### Song Filter")
        st.caption("Find exercises associated with specific songs")
        song_filter = st.text_input(
            "Filter by song:",
            help="Type part of a song title or artist name to find matching exercises",
            key="song_filter",
            placeholder="Enter song title or artist name...",
        )

        # Show info about song-based filtering
        if st.session_state.get("song_filter", "").strip():
            # Count exercises that match the filter
            from app.db.queries import get_exercises_by_song_name

            exercises = get_exercises_by_song_name(st.session_state.song_filter)
            count = len(exercises) if exercises else 0
            st.info(
                f"Found {count} exercises related to '{st.session_state.song_filter}'"
            )

            # Clear song filter button
            if st.button("Clear Song Filter"):
                st.session_state.song_filter = ""
                st.rerun()

        # Checkbox to hide/show Column 1
        st.session_state.show_exercise_selector = st.checkbox(
            "Show Available Exercises", value=st.session_state.get("show_exercise_selector", True)
        )

    # Define a helper function for rendering session components
    def render_session_components():
        # Session list first
        exercise_list.render_session_list()

        # Add a separator
        st.markdown("---")

        # Refactored Session Metadata section (now in the session list column)
        # Remove the old call to render_session_metadata_ui() here
        # Add another separator
        st.markdown("---")

        # Show saved sessions for loading
        if render_session_list_ui():
            st.rerun()

    # Conditional layout based on checkbox state
    if st.session_state.show_exercise_selector:
        # Two-column layout when exercise selector is shown
        col1, col2 = st.columns([1, 1])

        # Left column - Exercise selector
        with col1:
            exercise_added = exercise_selector.render_exercise_selector(selected_phase)
            if exercise_added:
                st.rerun()

        # Right column - Session components
        with col2:
            exercise_list.render_session_list()
            st.markdown("---")
            # Session Metadata Section
            session_metadata = st.session_state.session_metadata
            with st.expander("Session Metadata", expanded=False):
                # Session ID display (if exists)
                if session_metadata.get("id"):
                    st.text(f"Session ID: {session_metadata['id']}")
                # Last saved indicator
                if session_metadata.get("last_saved"):
                    from datetime import datetime
                    last_saved = datetime.fromisoformat(session_metadata["last_saved"])
                    st.text(f"Last saved: {last_saved.strftime('%H:%M:%S')}")
                # Session name field
                name = st.text_input(
                    "Session Name*",
                    value=session_metadata.get("name", ""),
                    key="session_name_input",
                )
                if name != session_metadata.get("name", ""):
                    session_metadata["name"] = name
                    mark_session_changed()
                # Date field
                date_val = session_metadata.get("date", None)
                from datetime import datetime
                date = st.date_input(
                    "Session Date",
                    value=datetime.strptime(date_val, "%Y-%m-%d") if date_val else datetime.now(),
                    key="session_date_input",
                )
                new_date = date.strftime("%Y-%m-%d")
                if new_date != session_metadata.get("date", ""):
                    session_metadata["date"] = new_date
                    mark_session_changed()
                # Description field
                description = st.text_area(
                    "Description",
                    value=session_metadata.get("description", ""),
                    key="session_description_input",
                )
                if description != session_metadata.get("description", ""):
                    session_metadata["description"] = description
                    mark_session_changed()
                # Tags field
                tags = st.text_input(
                    "Tags",
                    value=session_metadata.get("tags", ""),
                    help="Enter tags in #tag format, separated by spaces",
                    key="session_tags_input",
                )
                if tags != session_metadata.get("tags", ""):
                    session_metadata["tags"] = tags
                    mark_session_changed()
                # Only show clear button if we have an existing session
                if session_metadata.get("id"):
                    if st.button("Clear Form", key="clear_session_button"):
                        session_metadata.clear()
                        session_metadata.update({
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
                        })
                        st.rerun()
            # --- End of Expander ---
            # Unsaved changes alert below expander
            if session_metadata.get("has_unsaved_changes", False):
                st.warning("⚠️ Unsaved changes")
            # Save Session button below alert
            if st.button("Save Session", key="save_session_button"):
                success, _, _ = save_current_session(show_message=True)
                if success:
                    st.rerun()
            # Clear Session button (moved from sidebar)
            if st.button("Clear Session", key="clear_session_button_main"):
                st.session_state.session_exercises = []
                mark_session_changed()
                st.rerun()
            st.markdown("---")
            # Restore Load Session UI below metadata
            if render_session_list_ui():
                st.rerun()

    else:
        # Full-width layout when exercise selector is hidden
        # Place session list and metadata in sequence
        exercise_list.render_session_list()
        st.markdown("---")
        # --- Session Metadata Section (refactored, same as above) ---
        session_metadata = st.session_state.session_metadata
        with st.expander("Session Metadata", expanded=False):
            if session_metadata.get("id"):
                st.text(f"Session ID: {session_metadata['id']}")
            if session_metadata.get("last_saved"):
                from datetime import datetime
                last_saved = datetime.fromisoformat(session_metadata["last_saved"])
                st.text(f"Last saved: {last_saved.strftime('%H:%M:%S')}")
            name = st.text_input(
                "Session Name*",
                value=session_metadata.get("name", ""),
                key="session_name_input",
            )
            if name != session_metadata.get("name", ""):
                session_metadata["name"] = name
                mark_session_changed()
            date_val = session_metadata.get("date", None)
            from datetime import datetime
            date = st.date_input(
                "Session Date",
                value=datetime.strptime(date_val, "%Y-%m-%d") if date_val else datetime.now(),
                key="session_date_input",
            )
            new_date = date.strftime("%Y-%m-%d")
            if new_date != session_metadata.get("date", ""):
                session_metadata["date"] = new_date
                mark_session_changed()
            description = st.text_area(
                "Description",
                value=session_metadata.get("description", ""),
                key="session_description_input",
            )
            if description != session_metadata.get("description", ""):
                session_metadata["description"] = description
                mark_session_changed()
            tags = st.text_input(
                "Tags",
                value=session_metadata.get("tags", ""),
                help="Enter tags in #tag format, separated by spaces",
                key="session_tags_input",
            )
            if tags != session_metadata.get("tags", ""):
                session_metadata["tags"] = tags
                mark_session_changed()
            if session_metadata.get("id"):
                if st.button("Clear Form", key="clear_session_button"):
                    session_metadata.clear()
                    session_metadata.update({
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
                    })
                    st.rerun()
        if session_metadata.get("has_unsaved_changes", False):
            st.warning("⚠️ Unsaved changes")
        button_col1, button_col2 = st.columns([1, 1])
        with button_col1:
            if st.button("Save Session", key="save_session_button"):
                success, _, _ = save_current_session(show_message=True)
                if success:
                    st.rerun()
        with button_col2:
            if st.button("Clear Session", key="clear_session_button_main"):
                st.session_state.session_exercises = []
                mark_session_changed()
                st.rerun()
        st.markdown("---")
        # Restore Load Session UI below metadata
        if render_session_list_ui():
            st.rerun()


if __name__ == "__main__":
    main()
