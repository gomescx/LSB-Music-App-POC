As a user,
I want to generate a playlist file from all music files in the current session
So that I can easily import the playlist into Apple Music and play my selected songs without manual input

Acceptance Criteria (AC):

    Playlist Creation:
    The system generates a playlist file named <session name>.m3u in the current working directory.
    File Inclusion:
    The playlist includes all .mp3 and .m4a files found in the specified MUSIC_LIBRARY_PATH folder from the .env file.
    Relative Paths:
    Each entry in the playlist uses the absolute pat, eg. {MUSIC_LIBRARY_PATH}/filename.mp3

    M3U Format Compliance:
    The first line of the playlist is #EXTM3U to ensure compatibility with Apple Music.

    Compatibility:
    The generated .m3u file can be imported into Apple Music without errors, and all referenced songs appear in the new playlist if the files are accessible.

    Duplicates:
    Duplicates are allowed if duplicate filenames exist.

    File Ordering
    The playlist entries  are in the same sequence as the session musics




