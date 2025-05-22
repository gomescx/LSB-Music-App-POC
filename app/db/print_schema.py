from schema import get_db_connection

def print_all_table_schemas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?;", (table,))
        create_stmt = cursor.fetchone()[0]
        print(f"-- Schema for table: {table}\n{create_stmt}\n")

    conn.close()

if __name__ == "__main__":
    print_all_table_schemas()