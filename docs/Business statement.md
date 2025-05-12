
🔷 1. Business Value Proposition (POC)
--------------------------------------

**Problem**: Claudio, a veteran Biodanza teacher, faces delays and errors when manually building sessions using the LSB workbook, a flatfile music catalogue, and multiple disconnected tools (Word, Apple Music). He spends hours assembling sessions and troubleshooting song transitions — often having to redo documents and playlists.
**Solution**: Build a lightweight, local web app using Python and Streamlit to streamline session creation. The app will let Claudio:

* Browse and filter exercises grouped by session phases.

* Select and sequence exercises directly within the app.

* Preview and assign matching songs for each exercise.

* Play audio inline and export/share session output.

**Value**:

* **Immediate time savings** for upcoming classes and workshops.

* **Reduction in human error** in documentation and playlist building.

* **Improved musical cohesion** across sessions through better audio preview workflow.

* **Foundation for future growth**: searchable session archive, automated Apple Music playlist creation, mobile UX.

* * *

🔶 2. POC Delivery Plan for Azure DevOps Board
----------------------------------------------

## 🔱 Epic: LSB Music App – POC

> Goal: Deliver a local Streamlit web app that enables Claudio to assemble, preview, and export Biodanza sessions using the LSB exercise-to-song music catalogue.

## 🔹 Feature 1: Session Builder Core (POC Scope)

* * *
see file 'docs/User stories - All States.csv'
* * *

🛠 Tech Notes for Copilot Collaboration
---------------------------------------

Suggested queries for junior dev (Copilot):

* Song Filtering:

        df_filtered = df_songs[df_songs['exercise'].isin(card_df['exercise'])]
        

* Streamlit Audio Player:

        st.audio(f"./music_folder/{song_file_name}")
        

* Streamlit Dynamic Selection:

        selected_song = st.selectbox("Choose a song", list_of_songs)
        

* Save JSON Session:

        with open("sessions/my_session.json", "w") as f:
            json.dump(session_dict, f)
        
