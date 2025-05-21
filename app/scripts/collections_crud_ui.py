"""
CRUD UI for the collections table.
- Allows Create, Read, Update, Delete for collections
- 'LSB' collection is read-only and cannot be deleted
"""

import streamlit as st
import sys
from pathlib import Path

# Ensure app modules are importable
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent.parent
sys.path.insert(0, str(root_dir))
from app.db.schema import get_db_connection


def get_collections():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT collection_code, description FROM collections ORDER BY collection_code")
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_collection(collection_code, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO collections (collection_code, description) VALUES (?, ?)",
        (collection_code, description),
    )
    conn.commit()
    conn.close()


def update_collection(collection_code, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE collections SET description = ? WHERE collection_code = ?",
        (description, collection_code),
    )
    conn.commit()
    conn.close()


def delete_collection(collection_code):
    if collection_code == "LSB":
        return  # Never delete LSB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM collections WHERE collection_code = ?",
        (collection_code,),
    )
    conn.commit()
    conn.close()


def main():
    st.title("Collections Table CRUD UI")
    st.write("Manage collections. 'LSB' is read-only and cannot be deleted.")

    collections = get_collections()
    codes = [row[0] for row in collections]

    # List collections
    st.subheader("All Collections")
    for code, desc in collections:
        with st.expander(f"{code}"):
            st.text_input(
                "Collection Code", value=code, disabled=True, key=f"code_{code}"
            )
            if code == "LSB":
                st.text_input(
                    "Description", value=desc, disabled=True, key=f"desc_{code}"
                )
                st.info("This collection is read-only and cannot be deleted.")
            else:
                new_desc = st.text_input(
                    "Description", value=desc, key=f"desc_{code}"
                )
                if st.button(f"Update {code}", key=f"update_{code}"):
                    update_collection(code, new_desc)
                    st.success("Updated.")
                if st.button(f"Delete {code}", key=f"delete_{code}"):
                    delete_collection(code)
                    st.success("Deleted.")
                    st.rerun()

    # Add new collection
    st.subheader("Add New Collection")
    with st.form("add_collection_form"):
        new_code = st.text_input("Collection Code", max_chars=16)
        new_desc = st.text_input("Description")
        submitted = st.form_submit_button("Add Collection")
        if submitted:
            if not new_code or new_code in codes:
                st.error("Invalid or duplicate code.")
            else:
                add_collection(new_code, new_desc)
                st.success("Added.")
                st.rerun()

if __name__ == "__main__":
    main()
