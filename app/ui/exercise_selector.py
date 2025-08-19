"""
Exercise Selector UI component for LSB Music App.
"""
import streamlit as st
from app.db.queries import get_all_exercises, get_exercises_by_phase, get_exercises_by_song_name, get_exercises_by_cimeb_status
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
    
    # Check for Cimeb filter
    cimeb_filter = st.session_state.get("cimeb_filter", "All Exercises")
    
    song_filter = st.session_state.get("song_filter", "").strip()
    if song_filter:
        exercises = get_exercises_by_song_name(song_filter)
        st.info(
            f"🎵 Showing exercises related to song: '{song_filter}' (phase filter is ignored)"
        )
    else:
        # Apply Cimeb filtering first
        if cimeb_filter == "Cimeb Only":
            if phase == "All":
                exercises = get_exercises_by_cimeb_status(is_cimeb=True)
            else:
                all_cimeb = get_exercises_by_cimeb_status(is_cimeb=True)
                exercises = [ex for ex in all_cimeb if ex["phase"] == float(phase)]
        elif cimeb_filter == "Other Facilitators Only":
            if phase == "All":
                exercises = get_exercises_by_cimeb_status(is_cimeb=False)
            else:
                all_non_cimeb = get_exercises_by_cimeb_status(is_cimeb=False)
                exercises = [ex for ex in all_non_cimeb if ex["phase"] == float(phase)]
        else:
            # All exercises
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
        
        # Count Cimeb vs non-Cimeb exercises in this category
        cimeb_count = sum(1 for ex in category_exercises if ex["cimeb"])
        non_cimeb_count = len(category_exercises) - cimeb_count
        
        # Create category title with counts
        if cimeb_filter == "All Exercises" and non_cimeb_count > 0:
            category_title = f"{category} ({len(category_exercises)} exercises: {cimeb_count} Cimeb, {non_cimeb_count} Others)"
        else:
            category_title = f"{category} ({len(category_exercises)} exercises)"
        
        with st.expander(category_title):
            for ex in sorted_exercises:
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    # Add indicator for non-Cimeb exercises
                    if not ex["cimeb"]:
                        st.write(f"**{ex['name']}** [id {ex['id']}] 👥")
                        st.caption("🔹 From other facilitators")
                    else:
                        st.write(f"**{ex['name']}** [id {ex['id']}]")
                with col2:
                    if st.button("Add", key=f"add_{ex['id']}"):
                        add_exercise_to_session(ex)
                        return True
                with col3:
                    # Show source indicator
                    if ex["cimeb"]:
                        st.caption("🎯 Cimeb")
                    else:
                        st.caption("👥 Other")
    return False
