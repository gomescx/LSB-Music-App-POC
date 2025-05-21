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

from app.db.queries import (
    get_all_exercises,
    get_exercises_by_phase,
    get_songs_for_exercise,
    get_exercises_by_song_name,
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
    else:
        # Ensure all exercise tuples have the correct structure (with notes)
        for i, exercise_tuple in enumerate(st.session_state.session_exercises):
            if len(exercise_tuple) < 4:
                # Extract existing data
                if len(exercise_tuple) == 3:
                    exercise_name, music_ref, exercise_id = exercise_tuple
                    # Add empty notes to the tuple
                    st.session_state.session_exercises[i] = (
                        exercise_name,
                        music_ref,
                        exercise_id,
                        "",  # Empty notes
                    )
                # Handle legacy 2-element tuples if any exist
                elif len(exercise_tuple) == 2:
                    exercise_name, music_ref = exercise_tuple
                    # Extract ID from name if possible
                    exercise_id = None
                    if "[id " in exercise_name:
                        exercise_id = (
                            exercise_name.split("[id ")[1].split("]")[0].strip()
                        )
                    # Create new tuple with proper structure
                    st.session_state.session_exercises[i] = (
                        exercise_name,
                        music_ref,
                        exercise_id,
                        "",  # Empty notes
                    )

    if "open_expanders" not in st.session_state:
        st.session_state.open_expanders = set()

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
    # Create a tuple with exercise info, empty music placeholder, exercise ID, and empty notes
    exercise_tuple = (
        f"{exercise['name']} [id {exercise['id']}]",
        None,  # Music is None (blank) by default
        exercise["id"],  # Store the exercise ID for song retrieval
        "",  # Notes start as empty string
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

    # Get exercises based on song filter first (highest priority)
    song_filter = st.session_state.get("song_filter", "").strip()
    if song_filter:
        # When filtering by song, we ignore the phase filter
        exercises = get_exercises_by_song_name(song_filter)
        # Show a notice that song filter is taking precedence
        st.info(
            f"🎵 Showing exercises related to song: '{song_filter}' (phase filter is ignored)"
        )
    else:
        # If no song filter, apply normal phase filtering
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
        for exercise_tuple in st.session_state.session_exercises
        if exercise_tuple[1] is not None  # song_ref is at index 1
    )
    total_exercises = len(st.session_state.session_exercises)

    # Calculate total duration if there are songs
    total_minutes = 0
    total_seconds = 0

    for exercise_tuple in st.session_state.session_exercises:
        # Extract song_ref and exercise_id from tuple (indexes 1 and 2)
        song_ref = exercise_tuple[1]
        exercise_id = exercise_tuple[2]

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
        # Handle different tuple structures (with and without notes)
        if len(exercise_tuple) >= 4:
            exercise_name, selected_song, exercise_id, exercise_notes = exercise_tuple
        else:
            exercise_name, selected_song, exercise_id = exercise_tuple
            exercise_notes = ""  # Default empty notes

            # Immediately update the tuple to include notes to prevent data loss
            st.session_state.session_exercises[i] = (
                exercise_name,
                selected_song,
                exercise_id,
                exercise_notes,
            )

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

        # Check if this expander should be open based on session state
        if "open_expanders" not in st.session_state:
            st.session_state.open_expanders = set()

        # Create a unique key for this expander
        expander_key = f"expander_{i}_{exercise_id}"

        with st.expander(
            expander_title, expanded=(expander_key in st.session_state.open_expanders)
        ) as expanded:
            # Track the expanded state in session state
            if expanded:
                st.session_state.open_expanders.add(expander_key)
            elif expander_key in st.session_state.open_expanders:
                st.session_state.open_expanders.remove(expander_key)

            # First show the exercise name with ID for reference
            st.write(f"**Exercise:** {exercise_name}")

            # Add the control buttons at the top in a row for better visibility
            ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 1])

            with ctrl_col1:
                if st.button("↑ Move Up", key=f"up_{i}", disabled=(i == 0)):
                    # Preserve the expanded state for this exercise
                    if "open_expanders" not in st.session_state:
                        st.session_state.open_expanders = set()
                    # Get the exercise above that we're swapping with
                    if i > 0:
                        prev_exercise_name, _, prev_exercise_id = (
                            st.session_state.session_exercises[i - 1]
                        )
                        # Mark both expanders as open
                        st.session_state.open_expanders.add(
                            f"expander_{i}_{exercise_id}"
                        )
                        st.session_state.open_expanders.add(
                            f"expander_{i-1}_{prev_exercise_id}"
                        )
                    move_exercise_up(i)
                    st.rerun()

            with ctrl_col2:
                if st.button(
                    "↓ Move Down",
                    key=f"down_{i}",
                    disabled=(i == len(st.session_state.session_exercises) - 1),
                ):
                    # Preserve the expanded state for this exercise
                    if "open_expanders" not in st.session_state:
                        st.session_state.open_expanders = set()
                    # Get the exercise below that we're swapping with
                    if i < len(st.session_state.session_exercises) - 1:
                        next_exercise_name, _, next_exercise_id = (
                            st.session_state.session_exercises[i + 1]
                        )
                        # Mark both expanders as open
                        st.session_state.open_expanders.add(
                            f"expander_{i}_{exercise_id}"
                        )
                        st.session_state.open_expanders.add(
                            f"expander_{i+1}_{next_exercise_id}"
                        )
                    move_exercise_down(i)
                    st.rerun()

            with ctrl_col3:
                if st.button("✕ Remove", key=f"remove_{i}"):
                    # Clean up the expander state for this exercise
                    if "open_expanders" in st.session_state:
                        expander_key = f"expander_{i}_{exercise_id}"
                        if expander_key in st.session_state.open_expanders:
                            st.session_state.open_expanders.remove(expander_key)
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

                # # Add a "No song selected" option at the top
                # song_options = {"No song selected": None, **song_options}


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
                    # Ensure this expander stays open after rerun
                    expander_key = f"expander_{i}_{exercise_id}"
                    if "open_expanders" not in st.session_state:
                        st.session_state.open_expanders = set()
                    st.session_state.open_expanders.add(expander_key)

                    # Get notes from the tuple (should be at index 3)
                    # If not available, use empty string
                    notes = exercise_tuple[3] if len(exercise_tuple) >= 4 else ""

                    # Update the tuple with the new song reference and preserve notes
                    st.session_state.session_exercises[i] = (
                        exercise_name,
                        new_song_ref,
                        exercise_id,
                        notes,
                    )
                    mark_session_changed()
                    # Immediately rerun to update the UI
                    st.rerun()

                # Add notes text area for this exercise
                st.write("### Notes")
                notes_value = st.text_area(
                    "Add personal cues, observations, or choreography instructions:",
                    value=exercise_notes,
                    key=f"notes_{i}_{exercise_id}",
                    height=100,
                )

                # Update notes in session state if changed
                if notes_value != exercise_notes:
                    # Ensure this expander stays open after rerun
                    expander_key = f"expander_{i}_{exercise_id}"
                    if "open_expanders" not in st.session_state:
                        st.session_state.open_expanders = set()
                    st.session_state.open_expanders.add(expander_key)

                    # Update the tuple with new notes
                    st.session_state.session_exercises[i] = (
                        exercise_name,
                        selected_song,
                        exercise_id,
                        notes_value,
                    )
                    mark_session_changed()

                st.write("---")

                # Show song details if a song is selected
                if selected_song:
                    song_details = next(
                        (song for song in songs if song["music_ref"] == selected_song),
                        None,
                    )

                    if song_details:

                        # Generate the file path
                        file_path = get_song_file_path(song_details)

                        # Create a container for audio player with consistent height
                        audio_container = st.container()

                        # Add audio player if a valid file path exists
                        if file_path and not file_path.startswith("No music file"):
                            # Check if the file actually exists on disk
                            if os.path.exists(file_path):
                                try:
                                    with st.spinner("Loading audio..."):
                                        audio_container.audio(
                                            file_path, format="audio/*"
                                        )
                                except Exception as e:
                                    audio_container.error(
                                        f"Error playing audio: {str(e)}"
                                    )
                            else:
                                audio_container.warning(
                                    f"Audio file not found at location: `{os.path.basename(file_path)}`"
                                )
                        else:
                            audio_container.warning(
                                "No audio file available for this song"
                            )
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

                        # Display file path
                        st.write(f"• **File path:** `{file_path}`")

        # # Add a separator line between exercises for better visual separation
        # st.markdown("---")


# Remove any collection-related UI logic from here if present


def get_song_file_path(song_details):
    """
    Generate a file path for a song based on its metadata and the MUSIC_LIBRARY_PATH.

    Args:
        song_details: Dictionary containing song metadata from the database

    Returns:
        A string representing the file path to the song
    """
    if not song_details:
        return None

    # Get music library path from environment variables
    music_library_path = os.getenv("MUSIC_LIBRARY_PATH")

    # Generate a predictable path based on metadata
    # Use dictionary-style access for sqlite3.Row objects
    artist = song_details["artist"] if song_details["artist"] else "Unknown_Artist"
    artist = artist.replace(" ", "_")

    title = song_details["title"] if song_details["title"] else "Unknown_Title"
    title = title.replace(" ", "_")

    filename = song_details["filename"] if song_details["filename"] else ""
    filename = filename.replace(" ", "_")

    # If we have a filename use it, otherwise provide a message
    # indicating no file is available
    if filename:
        # Use the music library path from .env
        if music_library_path:
            return os.path.join(music_library_path, filename)
        else:
            return f"/sample_music_files/{filename}"
    else:
        return f"No music file available for {title} by {artist}"
