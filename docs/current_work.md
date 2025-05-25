As a user I want to see
    the vivencia lines and duration for any songs presented to me 
So 
    I can make better decisions when selecting the song compared to other songs
    

Acceptance Criteria (AC):

    - When there's a song on an exercise tuple, the vivencia lines are added at the end of it after the duration on the expander title
    - For the "Select a song:" drop down box, both the duration and vivencia lines are added after the artist
    - For the "Select any song from the catalogue:" drop down box, both the duration and vivencia lines are added after the artist


Notes for the Developer 
i) the term vivencia_line has not been depicted in this app yet. There are 5 vivencia_lines are v,s,c,a,t. each song can have 0 to 5 vivencia lines. these vivencia lines are depicted on the songs table by the fields v,s,c,a,t. whenever these fields have a value, it means that music has that vivencia line. i.e. if a row has values on columns v,c an dnot s,a,t it means the music has vivencia lines v,c
2) when presenting on the UI show with the following format: '🌀 [vivencia_lines in caps]' ,e.g. '🌀 [V,C]'
3) currenty the vivencia lines columns are not being read in any of the queries on app/db/queries.py
4) the songs are being displayed via app/ui/exercise_list.py 
5) add a 3rd column below the "Current Session"  to show how many occurences of each vivencia lines are selected in the songs, for instance, if there are 6 songs, 2 of them have V C, 3 of them have V, S, one of them has A, one has A , T the total would be:
V:5, S:3, C:2, A:2, T:1 and the system should show 
Vivencial Lines 🌀 [V:5 S:3 C:2 A:2 T:1]
always show in the order VSCAT
