"""
UI components and helper functions for the LSB Music App.
"""

import streamlit as st
import sys
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.db.queries import (
    get_all_exercises,
    get_exercises_by_phase,
    get_songs_for_exercise,
)
from app.sessions import (
    initialize_session_metadata,
    mark_session_changed,
    setup_autosave,
)


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "session_exercises" not in st.session_state:
        st.session_state.session_exercises = []

    # Initialize session metadata
    initialize_session_metadata()

    # Setup autosave functionality
    setup_autosave()


def add_exercise_to_session(exercise: Dict):
    """
    Add an exercise to the session.

    Args:
        exercise: The exercise to add (dict from database)
    """
    # Create a tuple with exercise info, empty music placeholder, and the exercise ID
    exercise_tuple = (
        f"{exercise['name']} [id {exercise['id']}]",
        None,  # Music is None (blank) by default
        exercise["id"],  # Store the exercise ID for song retrieval
    )

    # Add to session state
    st.session_state.session_exercises.append(exercise_tuple)

    # Mark session as changed for autosave
    mark_session_changed()


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

        # Mark session as changed for autosave
        mark_session_changed()


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

        # Mark session as changed for autosave
        mark_session_changed()


def remove_exercise(index: int):
    """
    Remove an exercise from the session list.

    Args:
        index: The index of the exercise to remove
    """
    st.session_state.session_exercises.pop(index)

    # Mark session as changed for autosave
    mark_session_changed()


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
    Render the current session list with reordering controls and song selection.
    """
    st.subheader("Current Session")

    if not st.session_state.session_exercises:
        st.info(
            "No exercises added to session yet. Use the selector above to add exercises."
        )
        return

    # Import here to avoid circular imports
    from app.db.queries import get_songs_for_exercise

    # Calculate session stats (songs selected and total time)
    total_songs = sum(
        1
        for _, song_ref, _ in st.session_state.session_exercises
        if song_ref is not None
    )
    total_exercises = len(st.session_state.session_exercises)

    # Calculate total duration if there are songs
    total_minutes = 0
    total_seconds = 0

    for _, song_ref, exercise_id in st.session_state.session_exercises:
        if song_ref is not None:
            songs = get_songs_for_exercise(exercise_id)
            song_details = next(
                (song for song in songs if song["music_ref"] == song_ref), None
            )
            if song_details and song_details["duration"]:
                duration_parts = song_details["duration"].split(":")
                if len(duration_parts) == 3:  # hh:mm:ss format
                    total_minutes += int(duration_parts[0]) * 60 + int(
                        duration_parts[1]
                    )
                    total_seconds += int(duration_parts[2])
                elif len(duration_parts) == 2:  # mm:ss format
                    total_minutes += int(duration_parts[0])
                    total_seconds += int(duration_parts[1])

    # Convert excess seconds to minutes
    total_minutes += total_seconds // 60
    total_seconds %= 60

    # Display the stats in a neat format with two columns
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Songs Selected:** {total_songs}/{total_exercises}")
    with col2:
        st.write(f"**Total Time:** {total_minutes}:{total_seconds:02d}")

    st.markdown("---")

    # Display each exercise with controls
    for i, exercise_tuple in enumerate(st.session_state.session_exercises):
        exercise_name, selected_song, exercise_id = exercise_tuple

        # Get songs for this exercise
        songs = get_songs_for_exercise(exercise_id)

        # Extract the display name without ID for cleaner UI
        display_name = (
            exercise_name.split(" [id ")[0]
            if " [id " in exercise_name
            else exercise_name
        )

        # Prepare the music and duration information for the expander title
        music_title = ""
        duration_text = ""

        if selected_song:
            song_details = next(
                (song for song in songs if song["music_ref"] == selected_song), None
            )
            if song_details:
                music_title = f"🎵 {song_details['title']}"
                # Format duration as mm:ss if available
                if song_details["duration"]:
                    # Convert duration from hh:mm:ss to mm:ss
                    duration_parts = song_details["duration"].split(":")
                    if len(duration_parts) == 3:  # If duration includes hours
                        duration_text = f" 🕒 {int(duration_parts[0]) * 60 + int(duration_parts[1]):02}:{int(duration_parts[2]):02}"
                    else:  # If duration is already mm:ss
                        duration_text = f" 🕒 {song_details['duration']}"
            else:
                music_title = "📂 No song selected"
        else:
            music_title = "📂 No song selected"

        # Create a single row with expander that includes all information
        expander_title = f"💃 {i+1}. {display_name}"
        if music_title:
            expander_title += f"    {music_title}"
        if duration_text:
            expander_title += f"    {duration_text}"

        with st.expander(expander_title, expanded=False):
            # First show the exercise name with ID for reference
            st.write(f"**Exercise:** {exercise_name}")

            # Add the control buttons at the top in a row for better visibility
            ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 1])

            with ctrl_col1:
                if st.button("↑ Move Up", key=f"up_{i}", disabled=(i == 0)):
                    move_exercise_up(i)
                    st.rerun()

            with ctrl_col2:
                if st.button(
                    "↓ Move Down",
                    key=f"down_{i}",
                    disabled=(i == len(st.session_state.session_exercises) - 1),
                ):
                    move_exercise_down(i)
                    st.rerun()

            with ctrl_col3:
                if st.button("✕ Remove", key=f"remove_{i}"):
                    remove_exercise(i)
                    st.rerun()

            # # Add song selection section
            # st.write("* * *")

            if not songs:
                st.write("No songs available for this exercise.")
            else:
                # Create a list of song options with formatted display
                song_options = {
                    f"{song['title']} - {song['artist']}": song["music_ref"]
                    for song in songs
                }

                # Add a "No song selected" option at the top
                song_options = {"No song selected": None, **song_options}

                # Get the current selection key
                current_key = "No song selected"
                if selected_song:
                    # Find the key for the currently selected song
                    for k, v in song_options.items():
                        if v == selected_song:
                            current_key = k
                            break

                # Create the selectbox for song selection
                selected_option = st.selectbox(
                    "Select a song:",
                    options=list(song_options.keys()),
                    key=f"song_select_{i}",
                    index=(
                        list(song_options.keys()).index(current_key)
                        if current_key in song_options
                        else 0
                    ),
                )

                # Update the session state when a song is selected
                new_song_ref = song_options[selected_option]
                if new_song_ref != selected_song:
                    # Update the tuple with the new song reference
                    st.session_state.session_exercises[i] = (
                        exercise_name,
                        new_song_ref,
                        exercise_id,
                    )
                    mark_session_changed()
                    # Immediately rerun to update the UI
                    st.rerun()

                # Show song details if a song is selected
                if selected_song:
                    song_details = next(
                        (song for song in songs if song["music_ref"] == selected_song),
                        None,
                    )

                    if song_details:
                        st.write("###### Song Details:")
                        st.write(f"• **Title:** {song_details['title']}")

                        # Display song details in two columns
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"• **Artist:** {song_details['artist']}")
                            if song_details["recommendation"]:
                                st.write(
                                    f"• **Recommendation:** {song_details['recommendation']}"
                                )

                        with col2:
                            st.write(f"• **Duration:** {song_details['duration']}")
                            st.write(f"• **BPM:** {song_details['bpm']}")

                        # Generate and display simulated file path
                        file_path = get_song_file_path(song_details)
                        st.write(f"• **File path:** `{file_path}`")

        # # Add a separator line between exercises for better visual separation
        # st.markdown("---")


def get_song_file_path(song_details):
    """
    Generate a simulated file path for a song based on its metadata.
    This is a placeholder function that will be replaced in Task 2.

    Args:
        song_details: Dictionary containing song metadata from the database

    Returns:
        A string representing the file path to the song
    """
    if not song_details:
        return None

    # Generate a predictable path based on metadata
    # Use dictionary-style access for sqlite3.Row objects
    artist = song_details["artist"] if song_details["artist"] else "Unknown_Artist"
    artist = artist.replace(" ", "_")

    title = song_details["title"] if song_details["title"] else "Unknown_Title"
    title = title.replace(" ", "_")

    filename = song_details["filename"] if song_details["filename"] else ""
    filename = filename.replace(" ", "_")

    # If we have a filename use it, otherwise construct from title and artist
    if filename:
        return f"/music_files/{filename}"
    else:
        return f"/music_files/{artist}/{title}.mp3"
