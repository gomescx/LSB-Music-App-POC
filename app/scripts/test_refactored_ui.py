"""
Test script for refactored UI logic in LSB Music App.
"""
import sys
from pathlib import Path
# Ensure project root is in sys.path for absolute imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
import streamlit as st

from app.ui import initialize_session_state
from app.ui import exercise_selector, exercise_list

def test_ui_components():
    initialize_session_state()
    st.write("Testing Exercise Selector:")
    exercise_selector.render_exercise_selector("All")
    st.write("Testing Session List:")
    exercise_list.render_session_list()

if __name__ == "__main__":
    test_ui_components()
