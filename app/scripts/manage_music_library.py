import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import sqlite3
from app.db.schema import get_db_connection

st.set_page_config(page_title="Manage Music Table", layout="wide")

st.title("🎵 Manage Music Library")
st.markdown("Use this tool to view, edit, or add songs to the music table.")

# --- Load existing music records from DB ---
def load_music_data():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM musics", conn)
    conn.close()
    return df

# --- Save updated records back to DB ---
def save_music_data(updated_df):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get all columns in musics table
        cursor.execute("PRAGMA table_info(musics)")
        table_columns = [row[1] for row in cursor.fetchall()]

        # Load current DB state
        db_df = pd.read_sql_query("SELECT * FROM musics", conn)

        # Helper to get next music_ref for a given collection_cd
        def get_next_music_ref(collection_cd):
            prefix = str(collection_cd)[:5]
            like_pattern = f"{prefix}-%"
            cursor.execute(
                "SELECT music_ref FROM musics WHERE music_ref LIKE ?", (like_pattern,)
            )
            existing_refs = cursor.fetchall()
            max_seq = 0
            for ref_tuple in existing_refs:
                ref = ref_tuple[0]
                try:
                    seq = int(ref.split('-')[-1])
                    if seq > max_seq:
                        max_seq = seq
                except Exception:
                    continue
            return f"{prefix}-{max_seq+1}"

        # Ensure all columns exist in updated_df
        for col in table_columns:
            if col not in updated_df.columns:
                updated_df[col] = None

        # Identify LSB rows in DB
        lsb_db = db_df[db_df['collection_code'] == 'LSB']
        # Only operate on non-LSB rows
        db_nonlsb = db_df[db_df['collection_code'] != 'LSB']
        updated_nonlsb = updated_df[updated_df['collection_code'] != 'LSB']

        # --- Detect deleted rows (in DB but not in updated, and not LSB) ---
        deleted = db_nonlsb[~db_nonlsb['music_ref'].isin(updated_nonlsb['music_ref'])]
        for _, row in deleted.iterrows():
            cursor.execute("DELETE FROM musics WHERE music_ref = ?", (row['music_ref'],))

        # --- Detect added rows (in updated but not in DB, and not LSB) ---
        added = updated_nonlsb[~updated_nonlsb['music_ref'].isin(db_nonlsb['music_ref'])].copy()
        # Generate music_ref for new rows and update in both DataFrame and insert
        for idx, row in added.iterrows():
            music_ref = row.get('music_ref', '')
            if not music_ref or pd.isna(music_ref):
                collection_cd = row.get('collection_cd', '')
                music_ref = get_next_music_ref(collection_cd)
                added.at[idx, 'music_ref'] = music_ref
                updated_df.loc[updated_df.index == row.name, 'music_ref'] = music_ref
            insert_cols = [col for col in table_columns if col in added.columns]
            insert_vals = [added.at[idx, col] for col in insert_cols]
            placeholders = ','.join(['?'] * len(insert_cols))
            cursor.execute(f"INSERT INTO musics ({','.join(insert_cols)}) VALUES ({placeholders})", insert_vals)

        # --- Detect updated rows (in both, not LSB, and changed) ---
        updated = []
        for _, row in updated_nonlsb.iterrows():
            if row['music_ref'] in db_nonlsb['music_ref'].values:
                db_row = db_nonlsb[db_nonlsb['music_ref'] == row['music_ref']].iloc[0]
                changed = any(row[col] != db_row[col] for col in table_columns if col != 'music_ref')
                if changed:
                    update_cols = [col for col in table_columns if col != 'music_ref']
                    set_clause = ', '.join([f"{col} = ?" for col in update_cols])
                    update_vals = [row[col] for col in update_cols] + [row['music_ref']]
                    cursor.execute(f"UPDATE musics SET {set_clause} WHERE music_ref = ?", update_vals)
                    updated.append(row)

        conn.commit()
        # --- Show summary ---
        st.success("Music table updated successfully!")
        if not added.empty:
            st.info("Added rows:")
            st.dataframe(added[table_columns])
        if updated:
            st.info("Updated rows:")
            st.dataframe(pd.DataFrame(updated)[table_columns])
        if not deleted.empty:
            st.info("Deleted rows:")
            st.dataframe(deleted[table_columns])
    except Exception as e:
        conn.rollback()
        st.error(f"Error updating music table: {e}")
    finally:
        conn.close()

# --- Display editable table ---
df_music = load_music_data()

# --- Filtering UI ---
# First line filters
first_line_columns = [
    "music_ref", "collection_cd", "title", "artist", "filename", "collection_code"
]
second_line_columns = ["v", "c", "a", "s", "t"]
filters = {}
st.subheader("Filter Music Table")
first_cols = st.columns(len(first_line_columns))
for idx, col in enumerate(first_line_columns):
    filters[col] = first_cols[idx].text_input(f"Filter {col}")

second_cols = st.columns(len(second_line_columns))
for idx, col in enumerate(second_line_columns):
    filters[col] = second_cols[idx].text_input(f"Filter {col}")

filtered_df = df_music.copy()
for col, val in filters.items():
    if val:
        filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(val, case=False, na=False)]

# --- Set rows with collection_code == 'LSB' as read-only ---
if 'collection_code' in filtered_df.columns:
    disabled_rows = filtered_df['collection_code'] == 'LSB'
else:
    disabled_rows = [False] * len(filtered_df)

edited_df = st.data_editor(
    filtered_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "music_ref": "Music Code",
        "collection_cd": "Collection CD (e.g., IBF-01)",
        "title": "Title",
        "artist": "Artist",
        "duration": "Duration (mm:ss)",
        "filename": "Filename",
        "v": "Vivencia Line V",
        "c": "Vivencia Line C",
        "a": "Vivencia Line A",
        "s": "Vivencia Line S",
        "t": "Vivencia Line T",
        "bpm": "Beats Per Minute",
        "collection_code": "Collection Code (e.g., LSB, KCA)"
    },
    disabled=["music_ref"]
)

if st.button("💾 Save Changes"):
    # Prevent saving if any LSB row was changed
    original_lsb = df_music[df_music['collection_code'] == 'LSB']
    edited_lsb = edited_df[edited_df['collection_code'] == 'LSB']
    # Compare only columns that exist in both
    common_cols = [col for col in original_lsb.columns if col in edited_lsb.columns]
    if not original_lsb[common_cols].equals(edited_lsb[common_cols]):
        st.error("You cannot edit rows where collection_code is 'LSB'. Please revert changes to these rows.")
    else:
        save_music_data(edited_df)
