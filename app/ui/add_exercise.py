"""
Add Exercise UI component for LSB Music App.
"""
import streamlit as st
from app.db.queries import add_new_exercise, get_next_exercise_id, get_all_exercise_categories
from app.sessions import mark_session_changed


def render_add_exercise_form():
    """Render the form for adding new exercises."""
    
    st.subheader("➕ Add New Exercise")
    st.caption("Add exercises from other facilitators to expand your session options")
    
    with st.form("add_exercise_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            exercise_name = st.text_input(
                "Exercise Name *",
                help="Full name of the exercise",
                placeholder="e.g., Creative Movement Flow"
            )
            
            exercise_phase = st.selectbox(
                "Phase *",
                options=[1.0, 2.0, 3.0, 4.0, 5.0],
                help="The Biodanza phase this exercise belongs to"
            )
            
        with col2:
            # Get existing categories for the selectbox
            categories = get_all_exercise_categories()
            category_names = [cat[0] for cat in categories] if categories else []
            
            # Allow user to select existing category or enter new one
            category_choice = st.radio(
                "Category",
                options=["Select existing", "Create new"],
                horizontal=True
            )
            
            if category_choice == "Select existing":
                exercise_category = st.selectbox(
                    "Exercise Category *",
                    options=category_names,
                    help="Category this exercise belongs to"
                )
            else:
                exercise_category = st.text_input(
                    "New Category *",
                    help="Enter a new category name",
                    placeholder="e.g., CREATIVE EXPRESSION"
                ).upper()
        
        exercise_short_name = st.text_input(
            "Short Name (optional)",
            help="Abbreviated name for the exercise",
            placeholder="e.g., CMF"
        )
        
        exercise_aka = st.text_input(
            "Also Known As (optional)",
            help="Alternative names for this exercise",
            placeholder="e.g., Flow Movement, Creative Dance"
        )
        
        exercise_notes = st.text_area(
            "Description/Notes (optional)",
            help="Additional information about the exercise",
            placeholder="Describe the exercise, its purpose, and any special instructions..."
        )
        
        # Indicate this is a non-Cimeb exercise
        st.info("💡 This exercise will be marked as **non-Cimeb** (created by other facilitators)")
        
        submitted = st.form_submit_button("Add Exercise", type="primary")
        
        if submitted:
            # Validate required fields
            if not exercise_name.strip():
                st.error("Exercise name is required")
                return False
                
            if not exercise_category.strip():
                st.error("Exercise category is required")
                return False
            
            # Get next available ID
            next_id = get_next_exercise_id()
            
            # Prepare exercise data
            exercise_data = {
                "id": next_id,
                "name": exercise_name.strip(),
                "phase": exercise_phase,
                "category": exercise_category.strip().upper(),
                "short_name": exercise_short_name.strip(),
                "aka": exercise_aka.strip(),
                "phase_reviewer": exercise_notes.strip(),
                "cimeb": 0  # Mark as non-Cimeb
            }
            
            # Add to database
            success = add_new_exercise(exercise_data)
            
            if success:
                st.success(f"✅ Exercise '{exercise_name}' added successfully with ID {next_id}")
                st.success("🔄 Refresh the page or clear filters to see the new exercise in the selector")
                
                # Store the exercise info in session state for the button outside the form
                st.session_state.last_added_exercise = {
                    "name": exercise_name,
                    "id": next_id
                }
                
                return True
            else:
                st.error("❌ Failed to add exercise. Please check the logs for details.")
                return False
    
    # Add to session button (outside the form)
    if st.session_state.get("last_added_exercise") and st.session_state.get("session_exercises") is not None:
        exercise_info = st.session_state.last_added_exercise
        add_to_session = st.button(
            f"Add '{exercise_info['name']}' to Current Session",
            key="add_to_session_button"
        )
        if add_to_session:
            exercise_tuple = (
                f"{exercise_info['name']} [id {exercise_info['id']}]",
                None,  # No music selected initially
                exercise_info['id'],
                "",  # No notes initially
            )
            st.session_state.session_exercises.append(exercise_tuple)
            mark_session_changed()
            st.success(f"Added to current session!")
            # Clear the last added exercise to hide the button
            del st.session_state.last_added_exercise
    
    return False


def render_exercise_management_sidebar():
    """Render the exercise management section in the sidebar."""
    
    st.markdown("### Exercise Management")
    
    # Toggle for showing add exercise form
    if "show_add_exercise" not in st.session_state:
        st.session_state.show_add_exercise = False
    
    # Button to toggle the add exercise form
    if st.button("➕ Add New Exercise", help="Add exercises from other facilitators"):
        st.session_state.show_add_exercise = not st.session_state.show_add_exercise
    
    # Show/hide filter for Cimeb vs non-Cimeb exercises
    cimeb_filter = st.radio(
        "Exercise Source:",
        options=["All Exercises", "Cimeb Only", "Other Facilitators Only"],
        help="Filter exercises by their source"
    )
    
    # Store the filter choice in session state
    st.session_state.cimeb_filter = cimeb_filter
    
    # Show info about current filter
    if cimeb_filter == "Cimeb Only":
        st.caption("🎯 Showing only official Cimeb exercises")
    elif cimeb_filter == "Other Facilitators Only":
        st.caption("👥 Showing only exercises from other facilitators")
    else:
        st.caption("📚 Showing all exercises")
