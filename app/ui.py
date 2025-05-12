"""
UI components and helper functions for the LSB Music App.
"""

import streamlit as st
import sys
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.db.queries import get_all_exercises, get_exercises_by_phase


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "session_exercises" not in st.session_state:
        st.session_state.session_exercises = []


def add_exercise_to_session(exercise: Dict):
    """
    Add an exercise to the session.

    Args:
        exercise: The exercise to add (dict from database)
    """
    # Create a tuple with exercise info and empty music placeholder
    exercise_tuple = (
        f"{exercise['name']} [id {exercise['id']}]",
        None,  # Music is None (blank) by default
    )

    # Add to session state
    st.session_state.session_exercises.append(exercise_tuple)


def move_exercise_up(index: int):
    """
    Move an exercise up in the session list.

    Args:
        index: The index of the exercise to move
    """
    if index > 0:
        # Swap with the exercise above
        (
            st.session_state.session_exercises[index],
            st.session_state.session_exercises[index - 1],
        ) = (
            st.session_state.session_exercises[index - 1],
            st.session_state.session_exercises[index],
        )


def move_exercise_down(index: int):
    """
    Move an exercise down in the session list.

    Args:
        index: The index of the exercise to move
    """
    if index < len(st.session_state.session_exercises) - 1:
        # Swap with the exercise below
        (
            st.session_state.session_exercises[index],
            st.session_state.session_exercises[index + 1],
        ) = (
            st.session_state.session_exercises[index + 1],
            st.session_state.session_exercises[index],
        )


def remove_exercise(index: int):
    """
    Remove an exercise from the session list.

    Args:
        index: The index of the exercise to remove
    """
    st.session_state.session_exercises.pop(index)


def render_exercise_selector(phase: str = "All"):
    """
    Render the exercise selector component.

    Args:
        phase: The phase to filter exercises by ("All" or a specific phase number as a string)

    Returns:
        The selected exercises
    """
    st.subheader("Available Exercises")

    # Get exercises based on phase
    if phase == "All":
        exercises = get_all_exercises()
    else:
        exercises = get_exercises_by_phase(float(phase))

    # Apply name filter if one is provided
    name_filter = st.session_state.get("name_filter", "").strip().upper()
    if name_filter:
        exercises = [ex for ex in exercises if name_filter in ex["name"].upper()]

    # Group exercises by category for better organization
    exercises_by_category = {}
    for ex in exercises:
        category = ex["category"]
        if category not in exercises_by_category:
            exercises_by_category[category] = []
        exercises_by_category[category].append(ex)

    # Sort categories alphabetically
    sorted_categories = sorted(exercises_by_category.keys())

    # Display exercises by category (sorted alphabetically)
    for category in sorted_categories:
        category_exercises = exercises_by_category[category]

        # Sort exercises within category by name
        sorted_exercises = sorted(category_exercises, key=lambda ex: ex["name"])

        with st.expander(f"{category} ({len(category_exercises)} exercises)"):
            for ex in sorted_exercises:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{ex['name']}** [id {ex['id']}]")

                with col2:
                    if st.button("Add", key=f"add_{ex['id']}"):
                        add_exercise_to_session(ex)
                        return True  # Indicate that an exercise was added

    return False  # No exercise was added


def render_session_list():
    """
    Render the current session list with reordering controls.
    """
    st.subheader("Current Session")

    if not st.session_state.session_exercises:
        st.info(
            "No exercises added to session yet. Use the selector above to add exercises."
        )
        return

    # Display each exercise with controls
    for i, (exercise_name, music) in enumerate(st.session_state.session_exercises):
        col1, col2, col3, col4, col5 = st.columns([1, 4, 1, 1, 1])

        # Sequence number
        with col1:
            st.write(f"**{i+1}.**")

        # Exercise name
        with col2:
            st.write(exercise_name)

        # Up button
        with col3:
            if st.button("↑", key=f"up_{i}", disabled=(i == 0)):
                move_exercise_up(i)
                st.rerun()

        # Down button
        with col4:
            if st.button(
                "↓",
                key=f"down_{i}",
                disabled=(i == len(st.session_state.session_exercises) - 1),
            ):
                move_exercise_down(i)
                st.rerun()

        # Remove button
        with col5:
            if st.button("✕", key=f"remove_{i}"):
                remove_exercise(i)
                st.rerun()
