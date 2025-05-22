"""
UI components and helper functions for the LSB Music App.
"""
import streamlit as st
import sys
import os
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.sessions import initialize_session_metadata, setup_autosave


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "session_exercises" not in st.session_state:
        st.session_state.session_exercises = []
    else:
        for i, exercise_tuple in enumerate(st.session_state.session_exercises):
            if len(exercise_tuple) < 4:
                if len(exercise_tuple) == 3:
                    exercise_name, music_ref, exercise_id = exercise_tuple
                    st.session_state.session_exercises[i] = (
                        exercise_name,
                        music_ref,
                        exercise_id,
                        "",
                    )
                elif len(exercise_tuple) == 2:
                    exercise_name, music_ref = exercise_tuple
                    exercise_id = None
                    if "[id " in exercise_name:
                        exercise_id = (
                            exercise_name.split("[id ")[1].split("]")[0].strip()
                        )
                    st.session_state.session_exercises[i] = (
                        exercise_name,
                        music_ref,
                        exercise_id,
                        "",
                    )
    if "open_expanders" not in st.session_state:
        st.session_state.open_expanders = set()
    initialize_session_metadata()
    setup_autosave()


# Only export initialize_session_state from this module
__all__ = ["initialize_session_state"]
