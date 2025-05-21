"""
Script to initialize the database and load the LSB catalogue data.
"""

import os
import sys
from pathlib import Path

# Make sure the app directory is in the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.data_loader import load_lsb_catalogue
from app.scripts.add_collections_support import main as run_collection_migration

def main():
    # Path to the Excel file
    excel_path = project_root / "input" / "LSB_Base_flatfile.xlsx"
    
    if not excel_path.exists():
        print(f"Error: Excel file not found at {excel_path}")
        return False
    
    # Make sure the data directory exists
    data_dir = project_root / "data"
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"Loading LSB catalogue from {excel_path}...")
    if load_lsb_catalogue(excel_path):
        db_path = data_dir / "lsb_catalogue.db"
        print(f"LSB catalogue loaded successfully to {db_path}!")
        run_collection_migration()  # Run the migration after loading
        return True
    else:
        print("Failed to load LSB catalogue.")
        return False

if __name__ == "__main__":
    main()
