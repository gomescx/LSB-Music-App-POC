"""
Shared UI components and helpers for LSB Music App.
"""
import os

def get_song_file_path(song_details):
    if not song_details:
        return None
    music_library_path = os.getenv("MUSIC_LIBRARY_PATH")
    artist = song_details["artist"] if song_details["artist"] else "Unknown_Artist"
    artist = artist.replace(" ", "_")
    title = song_details["title"] if song_details["title"] else "Unknown_Title"
    title = title.replace(" ", "_")
    filename = song_details["filename"] if song_details["filename"] else ""
    filename = filename.replace(" ", "_")
    if filename:
        if music_library_path:
            return os.path.join(music_library_path, filename)
        else:
            return f"/sample_music_files/{filename}"
    else:
        return f"No music file available for {title} by {artist}"
