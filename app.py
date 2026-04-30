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