import pandas as pd
from pathlib import Path

# Define the project root and path to the Excel file
project_root = Path(__file__).parent.parent.parent
excel_path = project_root / 'input' / 'LSB_Base_flatfile.xlsx'
excel = pd.ExcelFile(excel_path)

# Print sheet names
print(f"Sheets in the Excel file: {excel.sheet_names}")

# Examine each sheet
for sheet_name in excel.sheet_names:
    print(f"\n--- {sheet_name} ---")
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print("\nFirst 5 rows:")
    print(df.head().to_string())
    print("\n" + "-"*80)
