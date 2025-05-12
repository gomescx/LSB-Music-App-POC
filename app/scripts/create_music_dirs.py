"""
Script to create the music_files directory structure.
"""

import os
import sys
from pathlib import Path

# Make sure the app directory is in the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def create_music_dirs():
    """Create the music_files directory structure."""
    music_dir = project_root / "music_files"

    # Create main music directory
    os.makedirs(music_dir, exist_ok=True)

    # Create a README file with instructions
    readme_path = music_dir / "README.md"
    with open(readme_path, "w") as f:
        f.write(
            """# Music Files Directory

This directory is where your music files should be placed for the LSB Music App to find them.

## File Organization

The app will search for music files in the following order:

1. Using the exact filename from the database if available
2. Using a pattern of `Artist_Title.extension`
3. In artist subdirectories: `Artist/Title.extension`
4. Using a pattern of `Title_Artist.extension`

## Supported File Formats

The app supports the following audio formats:
- MP3 (.mp3)
- AAC/M4A (.m4a)
- WAV (.wav)
- FLAC (.flac)
- OGG Vorbis (.ogg)

## Sample Organization

Here's an example of how you might organize your files:

```
music_files/
├── Artist_Name/
│   ├── Song_Title_1.mp3
│   └── Song_Title_2.mp3
├── Another_Artist_Song_Title.mp3
└── Raw_Filename_From_Database.mp3
```

For best results, add all your music files to this directory before using the app.
"""
        )

    print(f"Created music files directory at {music_dir}")
    print(f"Added README.md with instructions")

    return True


if __name__ == "__main__":
    create_music_dirs()
