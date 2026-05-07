import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from main import get_ai_schedule, load_data, companyRoles 

# --- 1. PDF EXPORT LOGIC (Must be defined before use) ---
def export_to_pdf(schedule_text, date_str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16) # Use Helvetica as a standard safe font
    
    # Title
    pdf.cell(0, 10, f"SmartShift AI: Schedule for {date_str}", ln=True, align='C')
    pdf.ln(10)
    
    # Table Header
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(45, 10, "Name", border=1, fill=True)
    pdf.cell(45, 10, "Role", border=1, fill=True)
    pdf.cell(35, 10, "Start", border=1, fill=True)
    pdf.cell(35, 10, "End", border=1, fill=True)
    pdf.ln()
    
    # Parse the markdown table back into rows
    pdf.set_font("Helvetica", "", 10)
    lines = schedule_text.strip().split('\n')
    for line in lines:
        if '|' in line and '---' not in line and 'Employee Name' not in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 4:
                pdf.cell(45, 10, parts[0], border=1)
                pdf.cell(45, 10, parts[1], border=1)
                pdf.cell(35, 10, parts[2], border=1)
                pdf.cell(35, 10, parts[3], border=1)
                pdf.ln()
                
    return bytes(pdf.output()) # Removed .encode('latin-1') for modern fpdf2 compatibility

# --- 2. FILE & SESSION SETUP ---
ROLES_FILE = "roles.txt"

if not os.path.exists(ROLES_FILE):
    with open(ROLES_FILE, "w") as f:
        f.write("Manager\nChef\nCook\nWaiter\nBartender")

if "company_roles" not in st.session_state:
    with open(ROLES_FILE, "r") as f:
        st.session_state["company_roles"] = [line.strip() for line in f.readlines() if line.strip()]

# --- 3. UI CONFIGURATION ---
st.set_page_config(page_title="SmartShift AI", page_icon="📅", layout="wide")
st.title("🚀 SmartShift AI: Intelligent Scheduler")
st.markdown("Automate your team roles based on daily necessity and AI optimization.")

# --- 4. SIDEBAR ---
st.sidebar.header("Configuration")
mode = st.sidebar.toggle("Live AI Mode", value=True)

# Form: Add Staff
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
                df_team = pd.read_csv('team_availability.csv')
                new_member = {
                    "Name": new_name, "Default_Role": new_role, 
                    "Shift_Start": new_start, "Shift_End": new_end, 
                    "Max_Hours": 8, "Available_Monday": True, "Available_Friday": True
                }
                df_new = pd.concat([df_team, pd.DataFrame([new_member])], ignore_index=True)
                df_new.to_csv('team_availability.csv', index=False)
                st.sidebar.success(f"Added {new_name}!")
                st.rerun()
            except Exception as err:
                st.sidebar.error(f"Error: {err}")

# Form: Add Event
st.sidebar.divider()
st.sidebar.subheader("📅 Add New Event")
with st.sidebar.form("calendar_form", clear_on_submit=True):
    new_date = st.text_input("Date (YYYY-MM-DD)")
    new_event = st.text_input("Event Name")
    new_necessity = st.selectbox("Necessity Level", ["Low", "Medium", "High", "Very High"])
    new_min_staff = st.number_input("Min Staff", min_value=1, max_value=10, value=3)
    event_submitted = st.form_submit_button("Add Event")
    
    if event_submitted:
        try:
            df_calendar = pd.read_csv('calendar.csv')
            day_name = pd.to_datetime(new_date).day_name()
            new_row = {"Date": new_date, "Day": day_name, "Event_Type": new_event, "Necessity_Level": new_necessity, "Min_Staff_Required": new_min_staff}
            pd.concat([df_calendar, pd.DataFrame([new_row])], ignore_index=True).to_csv('calendar.csv', index=False)
            st.sidebar.success("Added Event!")
            st.rerun()
        except:
            st.sidebar.error("Check date format.")

# Form: Manage Roles
st.sidebar.divider()
st.sidebar.subheader("🛠️ Manage Roles")
with st.sidebar.form("role_form", clear_on_submit=True):
    new_role_input = st.text_input("New Role Name")
    if st.form_submit_button("Create Role") and new_role_input:
        clean_role = new_role_input.strip().title()
        if clean_role not in st.session_state["company_roles"]:
            st.session_state["company_roles"].append(clean_role)
            with open(ROLES_FILE, "w") as f:
                for r in st.session_state["company_roles"]: f.write(f"{r}\n")
            st.rerun()

with st.sidebar.form("delete_role_form", clear_on_submit=True):
    role_to_delete = st.selectbox("Remove Role", st.session_state["company_roles"])
    if st.form_submit_button("Delete Role"):
        st.session_state["company_roles"].remove(role_to_delete)
        with open(ROLES_FILE, "w") as f:
            for r in st.session_state["company_roles"]: f.write(f"{r}\n")
        st.rerun()

# --- 5. MAIN AREA ---
try:
    calendar, team = load_data()
    tab1, tab2 = st.tabs(["📅 Calendar View", "👥 Team Availability"])
    
    with tab1:
        st.subheader("Upcoming Calendar")
        st.dataframe(calendar, use_container_width=True)
        
    with tab2:
        st.subheader("Manage Team Members")
        edited_team = st.data_editor(team, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Save Changes"):
            edited_team.to_csv('team_availability.csv', index=False)
            st.rerun()

    st.divider()
    st.subheader("Generate New Schedule")
    selected_date = st.selectbox("Choose a date:", calendar['Date'])
    day_row = calendar[calendar['Date'] == selected_date].iloc[0]
    st.info(f"**Event:** {day_row['Event_Type']} | **Necessity:** {day_row['Necessity_Level']}")

    if st.button("Run AI Scheduler"):
        reqs = f"This is a {day_row['Event_Type']} with a {day_row['Necessity_Level']} necessity."
        with st.spinner("Calculating..."):
            # Store the output in session state so it survives the PDF download rerun
            st.session_state["final_output"] = get_ai_schedule(team, reqs, st.session_state["company_roles"])

    # Display schedule and download button if schedule exists
    if "final_output" in st.session_state:
        st.success("Schedule Generated!")
        st.markdown(st.session_state["final_output"])
        
        pdf_bytes = export_to_pdf(st.session_state["final_output"], selected_date)
        st.download_button(
            label="📄 Download Schedule as PDF",
            data=pdf_bytes,
            file_name=f"Schedule_{selected_date}.pdf",
            mime="application/pdf"
        )

except Exception as e:
    st.error(f"Error: {e}")