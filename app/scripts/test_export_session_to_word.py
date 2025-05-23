import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.scripts.export_session_to_word import export_session_to_word

def test_export_session_to_word():
    # Simulate session_metadata as a sqlite3.Row-like object
    class FakeRow(dict):
        def keys(self):
            return super().keys()
        def __getitem__(self, key):
            return super().__getitem__(key)
    # Example session metadata
    session_metadata = FakeRow({
        'id': 1,
        'name': 'Test Session',
        'description': 'A test session',
        'date': '2025-05-23',
        'tags': 'test,export',
        'version': 1,
        'created_at': '2025-05-23T10:00:00',
        'updated_at': '2025-05-23T10:00:00',
        'last_saved': '2025-05-23T10:00:00',
        'has_unsaved_changes': False
    })
    # Example session exercises
    session_exercises = [
        ('WALK WITH AFFECTIVE MOTIVATION', 'LSB27-02', 17, 'Warmup'),
        ('DANCE OF JOY', 'LSB15-01', 5, 'Main part'),
    ]
    # Use a temp export path
    export_path = os.path.abspath('./exports')
    result_path = export_session_to_word(session_metadata, session_exercises, export_path=export_path)
    print(f"Test export completed. File created at: {result_path}")

if __name__ == "__main__":
    test_export_session_to_word()
