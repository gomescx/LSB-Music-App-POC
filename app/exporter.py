import os
from dotenv import load_dotenv
from app.ui.components import get_song_file_path
from app.db.queries import get_all_songs

def export_playlist(session_name, session_exercises, export_path=None):
    """
    Generate an M3U playlist for the given session and save it to export_path.
    """
    load_dotenv()
    if export_path is None:
        export_path = os.getenv("EXPORT_PATH", os.getcwd())
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    all_songs = get_all_songs()
    song_paths = []
    for exercise_tuple in session_exercises:
        if len(exercise_tuple) >= 2:
            music_ref = exercise_tuple[1]
            if music_ref:
                song_details = next((s for s in all_songs if s["music_ref"] == music_ref), None)
                if song_details:
                    file_path = get_song_file_path(song_details)
                    if file_path and os.path.splitext(file_path)[1].lower() in [".mp3", ".m4a"]:
                        song_paths.append(file_path)
    if not song_paths:
        return None, 0
    playlist_filename = f"{session_name}.m3u"
    playlist_path = os.path.join(export_path, playlist_filename)
    with open(playlist_path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for path in song_paths:
            f.write(f"{path}\n")
    return playlist_path, len(song_paths)
