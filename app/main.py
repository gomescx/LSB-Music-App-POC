"""
LSB Music App - Main Streamlit App
"""

import streamlit as st
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.ui import (
    initialize_session_state,
    render_exercise_selector,
    render_session_list,
)
from app.sessions import (
    render_session_metadata_ui,
    render_session_list_ui,
)


def main():
    """Main function to run the Streamlit app."""
    # Set page title and icon
    st.set_page_config(page_title="LSB Music App", page_icon="🎵", layout="wide")

    # Initialize session state
    initialize_session_state()

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

        # Session info
        st.header("Session Details")
        st.write(f"Exercises in session: {len(st.session_state.session_exercises)}")

        # Session control buttons
        if st.button("Clear Session"):
            st.session_state.session_exercises = []
            # Mark session changed for autosave
            from app.sessions import mark_session_changed

            mark_session_changed()
            st.rerun()

        # Toggle for exercise selector visibility
        if "show_exercise_selector" not in st.session_state:
            st.session_state.show_exercise_selector = True

        # Create a callback for the checkbox
        def toggle_exercise_selector():
            st.session_state.show_exercise_selector = (
                not st.session_state.show_exercise_selector
            )

        # Use the checkbox with on_change callback
        st.checkbox(
            "Show Exercise Selector",
            value=st.session_state.show_exercise_selector,
            key="show_exercise_selector_checkbox",
            on_change=toggle_exercise_selector,
        )

    # Define a helper function for rendering session components
    def render_session_components():
        # Session list first
        render_session_list()

        # Add a separator
        st.markdown("---")

        # Then session metadata
        if render_session_metadata_ui():
            st.rerun()

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
            exercise_added = render_exercise_selector(selected_phase)
            if exercise_added:
                st.rerun()

        # Right column - Session components
        with col2:
            render_session_components()
    else:
        # Full-width layout when exercise selector is hidden
        render_session_components()


if __name__ == "__main__":
    main()
