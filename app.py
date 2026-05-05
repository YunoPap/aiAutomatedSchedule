import streamlit as st
import pandas as pd
import os
from main import get_ai_schedule, load_data, companyRoles # Import your existing logic

# Define the file where we will permanently save our roles
ROLES_FILE = "roles.txt"

# If the file doesn't exist, create it with your default roles
if not os.path.exists(ROLES_FILE):
    with open(ROLES_FILE, "w") as f:
        f.write("Manager\nChef\nCook\nWaiter\nBartender")

# Load roles from the text file into the app's session memory
if "company_roles" not in st.session_state:
    with open(ROLES_FILE, "r") as f:
        st.session_state["company_roles"] = [line.strip() for line in f.readlines() if line.strip()]

st.set_page_config(page_title="SmartShift AI", page_icon="📅", layout="wide")

st.title("🚀 SmartShift AI: Intelligent Scheduler")
st.markdown("Automate your team roles based on daily necessity and AI optimization.")

# ================= SIDEBAR SECTION =================
st.sidebar.header("Configuration")
mode = st.sidebar.toggle("Live AI Mode", value=True)

# --- 1. Form to Add Staff in Sidebar ---
st.sidebar.divider()
st.sidebar.subheader("👤 Add New Staff Member")

with st.sidebar.form("staff_form", clear_on_submit=True):
    new_name = st.text_input("Name")
    new_role = st.selectbox("Assign Default Role", st.session_state["company_roles"])
    new_start = st.text_input("Shift Start (e.g., 10:00)")
    new_end = st.text_input("Shift End (e.g., 18:00)")
    
    staff_submitted = st.form_submit_button("Add to Team")
    
    if staff_submitted:
        if new_name and new_start and new_end:
            try:
                # Load, append, and save
                df_team = pd.read_csv('team_availability.csv')
                new_member = {
                    "Name": new_name,
                    "Default_Role": new_role,
                    "Shift_Start": new_start,
                    "Shift_End": new_end,
                    "Max_Hours": 8, # Default value
                    "Available_Monday": True,
                    "Available_Friday": True
                }
                df_new = pd.concat([df_team, pd.DataFrame([new_member])], ignore_index=True)
                df_new.to_csv('team_availability.csv', index=False)
                
                st.sidebar.success(f"Added {new_name} to the roster!")
                st.rerun()
            except Exception as err:
                st.sidebar.error(f"Error updating team CSV: {err}")
        else:
            st.sidebar.error("Please fill out all employee fields.")


# --- 2. Form to Add Events in Sidebar ---
st.sidebar.divider()
st.sidebar.subheader("📅 Add New Event")

with st.sidebar.form("calendar_form", clear_on_submit=True):
    new_date = st.text_input("Date (YYYY-MM-DD)")
    new_event = st.text_input("Event Name (e.g., Brunch)")
    new_necessity = st.selectbox("Necessity Level", ["Low", "Medium", "High", "Very High"])
    new_min_staff = st.number_input("Min Staff Needed", min_value=1, max_value=10, value=3)
    
    event_submitted = st.form_submit_button("Add Event")
    
    if event_submitted:
        if new_date and new_event:
            try:
                # 1. Load existing calendar
                df_calendar = pd.read_csv('calendar.csv')
                
                # 2. Determine the Day name automatically using Pandas
                day_name = pd.to_datetime(new_date).day_name()
                new_event_row = {
                    "Date": new_date,
                    "Day": day_name,
                    "Event_Type": new_event,
                    "Necessity_Level": new_necessity,
                    "Min_Staff_Required": new_min_staff
                }
                
                # 3. Append and Save
                df_cal_new = pd.concat([df_calendar, pd.DataFrame([new_event_row])], ignore_index=True)
                df_cal_new.to_csv('calendar.csv', index=False)
                
                st.sidebar.success(f"Added {new_event} to calendar!")
                st.rerun()
            except Exception as date_err:
                st.sidebar.error("Invalid date format. Use YYYY-MM-DD")
        else:
            st.sidebar.error("Please fill out Date and Event name.")
        

# --- 3. Form to Add Roles in Sidebar ---
st.sidebar.divider()
st.sidebar.subheader("🛠️ Manage Roles")

with st.sidebar.form("role_form", clear_on_submit=True):
    new_role_input = st.text_input("New Role Name (e.g., Hostess)")
    role_submitted = st.form_submit_button("Create Role")
    
    if role_submitted:
        if new_role_input:
            clean_role = new_role_input.strip().title()
            if clean_role not in st.session_state["company_roles"]:
                st.session_state["company_roles"].append(clean_role)
                
                # --- NEW CODE: Write the new list of roles to the text file permanently ---
                with open(ROLES_FILE, "w") as f:
                    for r in st.session_state["company_roles"]:
                        f.write(f"{r}\n")
                
                st.sidebar.success(f"Role '{clean_role}' added and saved permanently!")
                st.rerun()
    
# --- 4. Form to Delete Roles in Sidebar ---
st.sidebar.divider()
st.sidebar.subheader("🗑️ Remove a Role")

with st.sidebar.form("delete_role_form", clear_on_submit=True):
    # Let the user pick which role to delete
    role_to_delete = st.selectbox("Select Role to Remove", st.session_state["company_roles"])
    delete_submitted = st.form_submit_button("Delete Role")
    
    if delete_submitted:
        if len(st.session_state["company_roles"]) > 1:
            # Remove from memory
            st.session_state["company_roles"].remove(role_to_delete)
            
            # Update the permanent file
            with open(ROLES_FILE, "w") as f:
                for r in st.session_state["company_roles"]:
                    f.write(f"{r}\n")
            
            st.sidebar.success(f"Role '{role_to_delete}' removed permanently!")
            st.rerun()
        else:
            st.sidebar.error("You must have at least one role available.")

# ================= MAIN AREA SECTION =================
try:
    # 1. Load Data
    calendar, team = load_data()

    # 2. Display Data Frames in Tabs
    tab1, tab2 = st.tabs(["📅 Calendar View", "👥 Team Availability"])
    
    with tab1:
        st.subheader("Upcoming Calendar")
        st.dataframe(calendar, use_container_width=True)
        
    with tab2:
        st.subheader("Manage Team Members")
        st.markdown("Edit existing employees in the table below, or use the sidebar to add new ones.")
        edited_team = st.data_editor(
            team, 
            use_container_width=True, 
            num_rows="dynamic",
            key="team_editor"
        )
        
        if st.button("💾 Save Changes to Team"):
            edited_team.to_csv('team_availability.csv', index=False)
            st.success("Changes saved successfully!")
            st.rerun()

    # 3. User Selection
    st.divider()
    st.subheader("Generate New Schedule")
    
    selected_date = st.selectbox("Choose a date from the calendar:", calendar['Date'])
    day_row = calendar[calendar['Date'] == selected_date].iloc[0]
    
    st.info(f"**Target Event:** {day_row['Event_Type']} | **Necessity Level:** {day_row['Necessity_Level']}")

    if st.button("Run AI Scheduler"):
        # Construct the requirement string dynamically
        reqs = f"This is a {day_row['Event_Type']} with a {day_row['Necessity_Level']} necessity level."
        
        with st.spinner("AI is calculating optimal shifts..."):
            # Call your function from main.py
            final_output = get_ai_schedule(team, reqs, st.session_state["company_roles"])

            st.success("Schedule Generated!")
            st.markdown(final_output)

except Exception as e:
    st.error(f"Setup Error: {e}")
    st.info("Check that your CSV files are in the project root folder.")