import streamlit as st
import pandas as pd
import os
from main import get_ai_schedule, load_data, companyRoles # Import your existing logic

st.set_page_config(page_title="SmartShift AI", page_icon="📅", layout="wide")

st.title("🚀 SmartShift AI: Intelligent Scheduler")
st.markdown("Automate your team roles based on daily necessity and AI optimization.")

# Sidebar - Settings & File Uploads
st.sidebar.header("Configuration")
mode = st.sidebar.toggle("Live AI Mode", value=True)
# Add this to app.py (usually in the sidebar section)

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
            # 1. Load existing calendar
            df_calendar = pd.read_csv('calendar.csv')
            
            # 2. Create the new row
            # We determine the Day name automatically using Pandas
            try:
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

try:
    # 1. Load Data
    calendar, team = load_data()

    # 2. Display Data Frames in Tabs
    tab1, tab2 = st.tabs(["📅 Calendar View", "👥 Team Availability"])
    with tab1:
        st.dataframe(calendar, use_container_width=True)
    with tab2:
        st.dataframe(team, use_container_width=True)

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
            # Call your existing function from main.py
            final_output = get_ai_schedule(team, reqs, companyRoles)
            
            st.success("Schedule Generated!")
            st.markdown(final_output)

except Exception as e:
    st.error(f"Setup Error: {e}")
    st.info("Check that your CSV files and .env are in the project root.")