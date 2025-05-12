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
        st.header("Filters")

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

        # Session info
        st.header("Session")
        st.write(f"Exercises in session: {len(st.session_state.session_exercises)}")

        # Session control buttons
        if st.button("Clear Session"):
            st.session_state.session_exercises = []
            st.rerun()

    # Main area - two columns
    col1, col2 = st.columns([1, 1])

    # Left column - Exercise selector
    with col1:
        exercise_added = render_exercise_selector(selected_phase)
        if exercise_added:
            st.rerun()

    # Right column - Session list
    with col2:
        render_session_list()


if __name__ == "__main__":
    main()
