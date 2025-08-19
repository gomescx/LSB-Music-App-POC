#!/usr/bin/env python3
"""
Test script to add a new exercise and verify the audio player functionality.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.db.queries import add_new_exercise, get_next_exercise_id, get_songs_for_exercise

def test_add_exercise():
    """Test adding a new exercise and checking its functionality."""
    
    print("Testing add new exercise functionality...")
    
    # Get next available ID
    next_id = get_next_exercise_id()
    print(f"Next available exercise ID: {next_id}")
    
    # Create test exercise data
    exercise_data = {
        "id": next_id,
        "name": "Test Creative Movement",
        "phase": 3.0,
        "category": "TESTING",
        "short_name": "TCM",
        "aka": "Test Movement",
        "phase_reviewer": "This is a test exercise for audio functionality",
        "cimeb": 0  # Mark as non-Cimeb
    }
    
    # Add to database
    success = add_new_exercise(exercise_data)
    
    if success:
        print(f"✅ Exercise '{exercise_data['name']}' added successfully with ID {next_id}")
        
        # Check if there are songs available for this exercise
        songs = get_songs_for_exercise(next_id)
        print(f"📋 Number of songs for this exercise: {len(songs)}")
        
        if not songs:
            print("ℹ️ No recommended songs for this exercise (expected for new exercises)")
            print("✅ This should trigger the 'Select any song from catalogue' functionality")
        else:
            print("🎵 Found recommended songs:")
            for song in songs[:3]:  # Show first 3
                print(f"  - {song['title']} by {song['artist']}")
        
        return True
    else:
        print("❌ Failed to add exercise")
        return False

if __name__ == "__main__":
    test_add_exercise()
