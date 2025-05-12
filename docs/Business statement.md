

🔷 1. Business Value Proposition (POC)
--------------------------------------

**Problem**: Claudio, a veteran Biodanza teacher, faces delays and errors when manually building sessions using the LSB workbook, a flatfile music catalogue, and multiple disconnected tools (Word, Apple Music). He spends hours assembling sessions and troubleshooting song transitions — often having to redo documents and playlists.
**Solution**: Build a lightweight, local web app using Python and Streamlit to streamline session creation. The app will let Claudio:
*   Browse and filter exercises grouped by session phases.
    
*   Select and sequence exercises directly within the app.
    
*   Preview and assign matching songs for each exercise.
    
*   Play audio inline and export/share session output.
    
**Value**:
*   **Immediate time savings** for upcoming classes and workshops.
    
*   **Reduction in human error** in documentation and playlist building.
    
*   **Improved musical cohesion** across sessions through better audio preview workflow.
    
*   **Foundation for future growth**: searchable session archive, automated Apple Music playlist creation, mobile UX.
    

* * *

🔶 2. POC Delivery Plan for Azure DevOps Board
----------------------------------------------

## 🔱 Epic: LSB Music App – POC

> Goal: Deliver a local Streamlit web app that enables Claudio to assemble, preview, and export Biodanza sessions using the LSB exercise-to-song music catalogue.



## 🔹 Feature 1: Session Builder Core (POC Scope)

### ✅ **User Story 1.1 – Load LSB Catalogue**

**As** a facilitator,  
**I want** the app to load the official LSB catalogue from a structured Excel workbook,  
**So that** I can browse official exercises and access their associated songs and phase information.
**Acceptance Criteria**:
*   Load Excel workbook (.xlsx) into the app on startup.
    
*   Extract exercises, phases, and song associations.
    
*   Structure data for in-app interaction.
    
🔧 **Tasks**:
*    Parse LSB workbook and extract catalogue data into internal format.
    
*    Normalize phase labels and exercise metadata.
    
*    Load and store song paths or filenames for playback.
    

* * *

### ✅ **User Story 1.2 – Select and Sequence Exercises via UI**

**As** a facilitator,  
**I want** to add and reorder exercises to build a session within the app,  
**So that** I can sequence my session without relying on an external CSV.
**Acceptance Criteria**:
*   Show available exercises grouped by phase (e.g., Opening, Activation, Integration).
    
*   Allow user to add an exercise to the session with one click.
    
*   Allow reordering exercises in the session list.
    
*   Show sequence numbers dynamically.
    
🔧 **Tasks**:
*    Build Streamlit UI to browse/filter exercises by phase.
    
*    Add “Add to Session” buttons with dynamic session panel.
    
*    Implement drag-and-drop or numeric input for sequencing.
    

* * *

### ✅ **User Story 1.3 – Select and Preview Song per Exercise**

**As** a facilitator,  
**I want** to preview and assign one song per exercise from a pre-filtered list,  
**So that** I can ensure musical flow and appropriateness before exporting the session.
**Acceptance Criteria**:
*   When an exercise is added to a session, show associated songs.
    
*   Let user click to play audio inline from local files.
    
*   Let user assign a selected song to that exercise.
    
*   Final session list includes each exercise with chosen song.
    
🔧 **Tasks**:
*    Show associated songs as selectbox/audio list per exercise.
    
*    Embed audio player for inline preview (using `st.audio`).
    
*    Track selected song for each session entry.
    

* * *

### ✅ **User Story 1.4 – Save and Load Past Sessions**

**As** a facilitator,  
**I want** to save my built session and reload it later,  
**So that** I can avoid rebuilding sessions from scratch and maintain a reusable archive.
**Acceptance Criteria**:
*   Save current session to structured local file (JSON/CSV).
    
*   Display list of past sessions in a dropdown.
    
*   Load and restore session details into the UI.
    
🔧 **Tasks**:
*    Implement JSON/CSV session save/load logic.
    
*    Create UI elements to list and load past sessions.
    
*    Ensure song file paths and order are preserved.
    

* * *

### 🟡 (Optional, Future) – Export Session (DOCX + Playlist)

#### 🎯 User Story – Export Session (Word + Playlist)

**As** a facilitator,  
**I want** to export the session to a Word document and text playlist,  
**So that** I can print or manually transfer it to Apple Music.

> _Note: This will be **deprioritized** if time constraints arise._

**Acceptance Criteria**:
*   Export a DOCX file with table: Exercise name, Vivencia Line, Selected Song.
    
*   Export a `.txt` or `.csv` with the ordered song filenames for easy Apple Music manual playlist creation.
    
**Tasks**:
*    Use `python-docx` for Word file generation.
    
*    Generate song list as plain text or CSV.
    
*    Save files locally under `exports/`.
    

* * *

🛠 Tech Notes for Copilot Collaboration
---------------------------------------

Suggested queries for junior dev (Copilot):
*   Song Filtering:
    
        df_filtered = df_songs[df_songs['exercise'].isin(card_df['exercise'])]
        
    
*   Streamlit Audio Player:
    
        st.audio(f"./music_folder/{song_file_name}")
        
    
*   Streamlit Dynamic Selection:
    
        selected_song = st.selectbox("Choose a song", list_of_songs)
        
    
*   Save JSON Session:
    
        with open("sessions/my_session.json", "w") as f:
            json.dump(session_dict, f)
        
    