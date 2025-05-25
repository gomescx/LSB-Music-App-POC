"""
Session Exercise List UI component for LSB Music App.
"""
import streamlit as st
import os
from app.db.queries import get_songs_for_exercise, get_all_songs, get_exercise_phase_by_id
from app.sessions import mark_session_changed
from .components import get_song_file_path

def move_exercise_up(index: int):
    if index > 0:
        (
            st.session_state.session_exercises[index],
            st.session_state.session_exercises[index - 1],
        ) = (
            st.session_state.session_exercises[index - 1],
            st.session_state.session_exercises[index],
        )
        mark_session_changed()

def move_exercise_down(index: int):
    if index < len(st.session_state.session_exercises) - 1:
        (
            st.session_state.session_exercises[index],
            st.session_state.session_exercises[index + 1],
        ) = (
            st.session_state.session_exercises[index + 1],
            st.session_state.session_exercises[index],
        )
        mark_session_changed()

def remove_exercise(index: int):
    st.session_state.session_exercises.pop(index)
    mark_session_changed()

def render_session_list():
    st.subheader("Current Session")
    if not st.session_state.session_exercises:
        st.info(
            "No exercises added to session yet. Use the selector above to add exercises."
        )
        return
    total_songs = sum(
        1
        for exercise_tuple in st.session_state.session_exercises
        if exercise_tuple[1] is not None
    )
    total_exercises = len(st.session_state.session_exercises)
    total_minutes = 0
    total_seconds = 0
    for exercise_tuple in st.session_state.session_exercises:
        song_ref = exercise_tuple[1]
        exercise_id = exercise_tuple[2]
        if song_ref is not None:
            songs = get_songs_for_exercise(exercise_id)
            song_details = next(
                (song for song in songs if song["music_ref"] == song_ref), None
            )
            if song_details and song_details["duration"]:
                duration_parts = song_details["duration"].split(":")
                if len(duration_parts) == 3:
                    total_minutes += int(duration_parts[0]) * 60 + int(duration_parts[1])
                    total_seconds += int(duration_parts[2])
                elif len(duration_parts) == 2:
                    total_minutes += int(duration_parts[0])
                    total_seconds += int(duration_parts[1])
    total_minutes += total_seconds // 60
    total_seconds %= 60
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Songs Selected:** {total_songs}/{total_exercises}")
    with col2:
        st.write(f"**Total Time:** {total_minutes}:{total_seconds:02d}")
    st.markdown("---")
    for i, exercise_tuple in enumerate(st.session_state.session_exercises):
        if len(exercise_tuple) >= 4:
            exercise_name, selected_song, exercise_id, exercise_notes = exercise_tuple
        else:
            exercise_name, selected_song, exercise_id = exercise_tuple
            exercise_notes = ""
            st.session_state.session_exercises[i] = (
                exercise_name,
                selected_song,
                exercise_id,
                exercise_notes,
            )
        songs = get_songs_for_exercise(exercise_id)
        phase = get_exercise_phase_by_id(exercise_id)
        phase_digits = list(str(int(phase))) if phase else []
        phase_text = f"[{','.join(phase_digits)}]" if phase_digits else "[ ]"
        song_options = {"📂 No song selected": None, "🎼 Custom music selection": "__custom__"}
        song_options.update({
            f"{song['title']} - {song['artist']}": song["music_ref"] for song in songs
        })
        display_name = (
            exercise_name.split(" [id ")[0]
            if " [id " in exercise_name
            else exercise_name
        )
        music_ref = selected_song
        music_title = ""
        duration_text = ""
        song_details = None
        if selected_song:
            song_details = next((song for song in songs if song["music_ref"] == selected_song), None)
            if not song_details:
                all_songs = get_all_songs()
                song_details = next((song for song in all_songs if song["music_ref"] == selected_song), None)
        if song_details:
            music_title = f"{song_details['title']}"
            if song_details["duration"]:
                duration_parts = song_details["duration"].split(":")
                if len(duration_parts) == 3:
                    duration_text = f" 🕒 {int(duration_parts[0]) * 60 + int(duration_parts[1]):02}:{int(duration_parts[2]):02}"
                else:
                    duration_text = f" 🕒 {song_details['duration']}"
        else:
            music_title = "📂 No song selected"
        expander_title = f"  💃 {i+1}. {display_name} ∿ {phase_text}"
        if music_title:
            expander_title += f"    🎵  {music_ref} {music_title}"
        if duration_text:
            expander_title += f"    {duration_text}"
        expander_key = f"expander_{i}_{exercise_id}"
        # Use a single open_expander_key instead of a set
        if "open_expander_key" not in st.session_state:
            st.session_state.open_expander_key = None
        with st.expander(
            expander_title, expanded=(st.session_state.open_expander_key == expander_key)
        ) as expanded:
            if expanded:
                # Set this as the only open expander
                st.session_state.open_expander_key = expander_key
            elif st.session_state.open_expander_key == expander_key:
                # If closed, clear the open expander key
                st.session_state.open_expander_key = None
            st.write(f"**Exercise:** {exercise_name}")
            ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([1, 1, 1, 2])
            with ctrl_col1:
                if st.button("↑ Move Up", key=f"up_{i}", disabled=(i == 0)):
                    # Keep the moved expander open
                    if i > 0:
                        prev_exercise_tuple = st.session_state.session_exercises[i - 1]
                        prev_exercise_id = prev_exercise_tuple[2]
                        st.session_state.open_expander_key = f"expander_{i-1}_{prev_exercise_id}"
                    move_exercise_up(i)
                    st.rerun()
            with ctrl_col2:
                if st.button(
                    "↓ Move Down",
                    key=f"down_{i}",
                    disabled=(i == len(st.session_state.session_exercises) - 1),
                ):
                    if i < len(st.session_state.session_exercises) - 1:
                        next_exercise_tuple = st.session_state.session_exercises[i + 1]
                        next_exercise_id = next_exercise_tuple[2]
                        st.session_state.open_expander_key = f"expander_{i+1}_{next_exercise_id}"
                    move_exercise_down(i)
                    st.rerun()
            with ctrl_col3:
                if st.button("✕ Remove", key=f"remove_{i}"):
                    # If removing the open expander, clear the key
                    if st.session_state.open_expander_key == expander_key:
                        st.session_state.open_expander_key = None
                    remove_exercise(i)
                    st.rerun()
            with ctrl_col4:
                new_position = st.number_input(
                    "Order",
                    min_value=1,
                    max_value=len(st.session_state.session_exercises),
                    value=i+1,
                    key=f"order_input_{i}_{exercise_id}",
                    step=1,
                )
                if new_position != i+1:
                    exercises = st.session_state.session_exercises
                    tuple_to_move = exercises.pop(i)
                    insert_at = new_position - 1
                    if insert_at > i:
                        insert_at -= 1
                    exercises.insert(insert_at, tuple_to_move)
                    st.session_state.open_expander_key = f"expander_{insert_at}_{exercise_id}"
                    mark_session_changed()
                    st.rerun()
            if not songs:
                st.write("No songs available for this exercise.")
            else:
                song_options = {"🎼 Custom music selection": "__custom__"}
                song_options.update({
                    f"{song['title']} - {song['artist']}": song["music_ref"] for song in songs
                })
                if selected_song is None:
                    current_key = "📂 No song selected"
                else:
                    for k, v in song_options.items():
                        if v == selected_song:
                            current_key = k
                            break
                    else:
                        all_songs = get_all_songs()
                        for song in all_songs:
                            if song["music_ref"] == selected_song:
                                current_key = f"{song['title']} - {song['artist']}"
                                break
                        else:
                            current_key = "📂 No song selected"
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
                if song_options[selected_option] == "__custom__":
                    all_songs = get_all_songs()
                    custom_filter = st.text_input(
                        "Filter songs by title:", "", key=f"custom_song_filter_{i}"
                    )
                    filtered_songs = [
                        song for song in all_songs if custom_filter.lower() in song["title"].lower()
                    ]
                    custom_song_options = {
                        f"{song['title']} - {song['artist']}": song["music_ref"] for song in filtered_songs
                    }
                    custom_current_key = "-- Select a song --"
                    if selected_song:
                        for k, v in custom_song_options.items():
                            if v == selected_song:
                                custom_current_key = k
                                break
                    custom_selected = st.selectbox(
                        "Select any song from the catalogue:",
                        options=["-- Select a song --"] + list(custom_song_options.keys()),
                        key=f"custom_song_select_{i}",
                        index=(
                            ["-- Select a song --"] + list(custom_song_options.keys())
                        ).index(custom_current_key) if custom_current_key in ["-- Select a song --"] + list(custom_song_options.keys()) else 0
                    )
                    if custom_selected != "-- Select a song --":
                        new_song_ref = custom_song_options[custom_selected]
                        if new_song_ref != selected_song:
                            st.session_state.open_expander_key = expander_key
                            notes = exercise_tuple[3] if len(exercise_tuple) >= 4 else ""
                            st.session_state.session_exercises[i] = (
                                exercise_name,
                                new_song_ref,
                                exercise_id,
                                notes,
                            )
                            mark_session_changed()
                            st.rerun()
                elif song_options[selected_option] is not None:
                    new_song_ref = song_options[selected_option]
                    if new_song_ref != selected_song:
                        st.session_state.open_expander_key = expander_key
                        notes = exercise_tuple[3] if len(exercise_tuple) >= 4 else ""
                        st.session_state.session_exercises[i] = (
                            exercise_name,
                            new_song_ref,
                            exercise_id,
                            notes,
                        )
                        mark_session_changed()
                        st.rerun()
                else:
                    if selected_song is not None:
                        st.session_state.open_expander_key = expander_key
                        notes = exercise_tuple[3] if len(exercise_tuple) >= 4 else ""
                        st.session_state.session_exercises[i] = (
                            exercise_name,
                            None,
                            exercise_id,
                            notes,
                        )
                        mark_session_changed()
                        st.rerun()
                st.write("### Notes")
                notes_value = st.text_area(
                    "Add personal cues, observations, or consigna instructions:",
                    value=exercise_notes,
                    key=f"notes_{i}_{exercise_id}",
                    height=100,
                )
                if notes_value != exercise_notes:
                    st.session_state.open_expander_key = expander_key
                    st.session_state.session_exercises[i] = (
                        exercise_name,
                        selected_song,
                        exercise_id,
                        notes_value,
                    )
                    mark_session_changed()
                st.write("---")
                song_details = None
                if selected_song:
                    song_details = next((song for song in songs if song["music_ref"] == selected_song), None)
                    if not song_details:
                        all_songs = get_all_songs()
                        song_details = next((song for song in all_songs if song["music_ref"] == selected_song), None)
                if song_details:
                    file_path = get_song_file_path(song_details)
                    audio_container = st.container()
                    if file_path and not file_path.startswith("No music file"):
                        if os.path.exists(file_path):
                            # Use a session state flag to remember if the audio was loaded for this exercise
                            audio_key = f"audio_loaded_{i}"
                            if audio_key not in st.session_state:
                                st.session_state[audio_key] = False
                            if not st.session_state[audio_key]:
                                load_audio = audio_container.button("Load Audio Player", key=f"load_audio_{i}")
                                if load_audio:
                                    # Reset all other audio_loaded flags except for this one
                                    for j in range(len(st.session_state.session_exercises)):
                                        other_audio_key = f"audio_loaded_{j}"
                                        st.session_state[other_audio_key] = (j == i)
                                    st.session_state.open_expander_key = expander_key  # Ensure this expander stays open
                                    st.rerun()
                            if st.session_state[audio_key]:
                                try:
                                    with st.spinner("Loading audio..."):
                                        audio_container.audio(file_path, format="audio/*")
                                except Exception as e:
                                    audio_container.error(f"Error playing audio: {str(e)}")
                        else:
                            audio_container.warning(f"Audio file not found at location: `{os.path.basename(file_path)}`")
                    else:
                        audio_container.warning("No audio file available for this song")
                    st.write("###### Song Details:")
                    st.write(f"• **Title:** {song_details['music_ref']} {song_details['title']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"• **Artist:** {song_details['artist']}")
                        recommendation = None
                        try:
                            recommendation = song_details['recommendation']
                        except (KeyError, IndexError):
                            pass
                        if recommendation:
                            st.write(f"• **Recommendation:** {recommendation}")
                    with col2:
                        duration_parts = song_details["duration"].split(":")
                        duration_text = f" 🕒 {int(duration_parts[0]) * 60 + int(duration_parts[1]):02}:{int(duration_parts[2]):02}"
                        st.write(f"• **Duration:** {duration_text}")
                        st.write(f"• **BPM:** {song_details['bpm']}")
                    st.write(f"• **File path:** `{file_path}`")
    # Export Playlist Button (after session stats, before exercises)
    session_name = st.session_state.session_metadata.get("name", "Session")
    export_clicked = st.button("Export Playlist (.m3u)", key="export_playlist_button")
    if export_clicked:
        from app.exporter import export_playlist
        export_path, song_count = export_playlist(
            session_name=session_name,
            session_exercises=st.session_state.session_exercises
        )
        if export_path and song_count > 0:
            st.success(f"Playlist exported to: {export_path} ({song_count} songs)")
        else:
            st.warning("No valid .mp3 or .m4a songs found in session. Playlist not created.")
    # Export Session to Word Button (after playlist export)
    export_word_clicked = st.button("Export Session to Word (.docx)", key="export_word_button")
    if export_word_clicked:
        from app.scripts.export_session_to_word import export_session_to_word
        session_metadata = st.session_state.session_metadata
        session_exercises = st.session_state.session_exercises
        try:
            word_path = export_session_to_word(session_metadata, session_exercises)
            st.success(f"Session exported to Word: {word_path}")
        except Exception as e:
            st.error(f"Failed to export session to Word: {e}")
