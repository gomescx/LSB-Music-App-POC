US 111 - Export Session Exercise - Music List to MS Word
As a user I want to export the current session into a MS Word file
So 

    I can run the session without having to fire up the python systems
    I can share my session with other facilitators

Acceptance Criteria (AC):

    The user clicks on a button and a MS Word file is generated on the path defined by EXPORT_PATH inside .env
    The MS Word file has the followign information
        all fields displayed on the UI as metadata
        a table listing all exercise - music tuples with the following columns: [#, Exercise, Music, Duration, Notes] where:
            # = sequence order, e.g. 3 if it's the third exercise - tuple of the list
            Exercise.name +  Exercise.id e.g. 'WALK WITH AFFECTIVE MOTIVATION [id 17]'
            music.music_ref + ' ' + music.title + ' {music.artist}}' e.g.LSB27-02 Somewhere Over the Rainbow-Wonderful World {Israel Kamakawiwo'Ole}
            music.duration in mm:ss
            session_exercises.notes






