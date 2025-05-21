🔧 Task Title: Extend Data Model to Support Music Collections
📄 Description:

Update the database schema to support multiple music collections (e.g., LSB, KCA, MAU). This change will allow the app to distinguish between official catalogue content and user-added or facilitator-specific collections.
🛠 Scope:

    Create a new table collections:

        Fields:

            collection_code (VARCHAR(3), PRIMARY KEY)

            description (TEXT)

        Insert the initial record:
        ['LSB', 'London School of Biodanza']

    Update the music table:

        Add a new column: collection_code (VARCHAR(3), FOREIGN KEY to collections)

        Populate all existing rows with the value 'LSB'

    Update the exercise_music_mapping table:

        Add a new column: collection_code (VARCHAR(3), FOREIGN KEY to collections)

        Populate all existing rows with the value 'LSB'

✅ Acceptance Criteria:

    A new collections table is created and contains at least one row for 'LSB'.

    Both music and exercise_music_mapping tables have a new collection_code column.

    All current data in music and exercise_music_mapping is updated with 'LSB'.

    Foreign key constraints are properly applied and enforce integrity.

