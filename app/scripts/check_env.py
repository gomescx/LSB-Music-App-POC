"""
Script to check environment variables and music file paths.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Make sure the app directory is in the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables from .env file
load_dotenv()


def check_env_variables():
    """Check environment variables and music paths."""
    print("\nChecking environment variables:")

    # Check MUSIC_LIBRARY_PATH
    music_library_path = os.getenv("MUSIC_LIBRARY_PATH")
    if music_library_path:
        print(f"✓ MUSIC_LIBRARY_PATH: {music_library_path}")

        # Check if path exists
        if os.path.exists(music_library_path):
            print(f"✓ Path exists")

            # Count music files
            music_files = [
                f
                for f in os.listdir(music_library_path)
                if f.endswith((".mp3", ".m4a", ".wav"))
            ]
            print(f"✓ Found {len(music_files)} music files")

            # Show a few examples
            if music_files:
                print("\nSample files:")
                for i, file in enumerate(sorted(music_files)[:5]):
                    print(f"  {i+1}. {file}")
                    full_path = os.path.join(music_library_path, file)
                    print(f"     Full path: {full_path}")
                    print(f"     Exists: {os.path.exists(full_path)}")
        else:
            print(f"✗ Path does not exist: {music_library_path}")
    else:
        print("✗ MUSIC_LIBRARY_PATH not found in environment")


if __name__ == "__main__":
    check_env_variables()
