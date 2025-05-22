

### 🔖 **User Story Title**

**Allow Custom Music Selection for Any Exercise**

---

### 📜 **User Story**

**As a** facilitator,
**I want** the ability to select any song from the entire music catalogue for a given exercise,
**So that** I can have more flexibility and musical variety when building a session.

---

### ✅ **Acceptance Criteria**

1. When selecting music for an exercise, the UI presents an option called **"Custom music selection"** at the top of the song dropdown list.
2. If the user selects this option:

   * A searchable dropdown or selection table is displayed.
   * The user can filter songs using **partial title text**.
   * The list includes **all songs** in the catalogue, not limited by predefined exercise-song mappings.
3. Once selected, the song is assigned to the current exercise within the session.

---

### 🛠 **Developer Notes**

* In `ui.py`, inside the `render_session_list()` function:

  * Modify the song dropdown for each exercise to include `"Custom music selection"` as the first option.
  * When selected, override the default mapping-based filter logic.
  * Display a searchable component (dropdown or AgGrid) that allows selecting any song by title substring match.
  * Ensure song assignment logic handles both mapped and custom selections consistently.


