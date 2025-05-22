"""
Exercise Selector UI component for LSB Music App.
"""
import streamlit as st
from app.db.queries import get_all_exercises, get_exercises_by_phase, get_exercises_by_song_name
from app.sessions import mark_session_changed
from typing import Dict

def add_exercise_to_session(exercise: Dict):
    exercise_tuple = (
        f"{exercise['name']} [id {exercise['id']}]",
        None,
        exercise["id"],
        "",
    )
    st.session_state.session_exercises.append(exercise_tuple)
    mark_session_changed()

def render_exercise_selector(phase: str = "All"):
    st.subheader("Available Exercises")
    song_filter = st.session_state.get("song_filter", "").strip()
    if song_filter:
        exercises = get_exercises_by_song_name(song_filter)
        st.info(
            f"🎵 Showing exercises related to song: '{song_filter}' (phase filter is ignored)"
        )
    else:
        if phase == "All":
            exercises = get_all_exercises()
        else:
            exercises = get_exercises_by_phase(float(phase))
    name_filter = st.session_state.get("name_filter", "").strip().upper()
    if name_filter:
        exercises = [ex for ex in exercises if name_filter in ex["name"].upper()]
    exercises_by_category = {}
    for ex in exercises:
        category = ex["category"]
        if category not in exercises_by_category:
            exercises_by_category[category] = []
        exercises_by_category[category].append(ex)
    sorted_categories = sorted(exercises_by_category.keys())
    for category in sorted_categories:
        category_exercises = exercises_by_category[category]
        sorted_exercises = sorted(category_exercises, key=lambda ex: ex["name"])
        with st.expander(f"{category} ({len(category_exercises)} exercises)"):
            for ex in sorted_exercises:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{ex['name']}** [id {ex['id']}]")
                with col2:
                    if st.button("Add", key=f"add_{ex['id']}"):
                        add_exercise_to_session(ex)
                        return True
    return False
