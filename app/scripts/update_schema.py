"""
Script to update the database schema with session tables.
"""

import sys
from pathlib import Path

# Make sure the app directory is in the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.db.schema import init_db


def main():
    """Update the database schema with session tables."""
    print("Updating database schema...")
    if init_db():
        print("Database schema updated successfully!")
        print("The new schema includes tables for session management.")
        return True
    else:
        print("Failed to update database schema.")
        return False


if __name__ == "__main__":
    main()
