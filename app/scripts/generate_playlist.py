"""
Generate an M3U playlist from the current session's selected songs.

Usage:
    source .venv/bin/activate
    python app/scripts/generate_playlist.py [--session SESSION_NAME]

- The playlist will be named <session name>.m3u and saved in the current directory.
- Only .mp3 and .m4a files from MUSIC_LIBRARY_PATH will be included.
- The order of songs matches the session order.
- Duplicates are allowed.
- The first line of the playlist is #EXTM3U.

If --session is not provided, the most recently updated session will be used.
"""
import os
import sys
from pathlib import Path
import argparse
from dotenv import load_dotenv

# Ensure app/ is in path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.db.queries import get_all_sessions, get_session_by_id, get_all_songs
from app.ui.components import get_song_file_path

def get_latest_session():
    sessions = get_all_sessions()
    if not sessions:
        raise RuntimeError("No saved sessions found.")
    # Sort by updated_at descending
    sessions = sorted(sessions, key=lambda s: s.get("updated_at") or s.get("date") or "", reverse=True)
    return sessions[0]

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Generate M3U playlist from session.")
    parser.add_argument("--session", type=str, help="Session name to export (default: latest)")
    args = parser.parse_args()

    music_library_path = os.getenv("MUSIC_LIBRARY_PATH")
    if not music_library_path or not os.path.exists(music_library_path):
        print("Error: MUSIC_LIBRARY_PATH is not set or does not exist.")
        sys.exit(1)

    # Find session
    if args.session:
        sessions = get_all_sessions()
        session = next((s for s in sessions if s["name"] == args.session), None)
        if not session:
            print(f"Session '{args.session}' not found.")
            sys.exit(1)
    else:
        session = get_latest_session()

    session_id = session["id"]
    session_name = session["name"]
    session_data, session_exercises = get_session_by_id(session_id)

    # Collect song file paths in order
    song_paths = []
    for exercise_tuple in session_exercises:
        if len(exercise_tuple) >= 2:
            music_ref = exercise_tuple[1]
            if music_ref:
                # Find song details
                all_songs = get_all_songs()
                song_details = next((s for s in all_songs if s["music_ref"] == music_ref), None)
                if song_details:
                    file_path = get_song_file_path(song_details)
                    if file_path and os.path.splitext(file_path)[1].lower() in [".mp3", ".m4a"]:
                        song_paths.append(file_path)

    if not song_paths:
        print("No valid .mp3 or .m4a songs found in session.")
        sys.exit(1)

    # Write M3U file
    playlist_filename = f"{session_name}.m3u"
    with open(playlist_filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for path in song_paths:
            f.write(f"{path}\n")
    print(f"Playlist written to {playlist_filename} with {len(song_paths)} songs.")

if __name__ == "__main__":
    main()
