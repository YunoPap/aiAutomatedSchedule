import re
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

try:
    import openai
except ImportError:
    openai = None

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)  # Explicitly load the .env in the project root
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_OPENAI = os.getenv("USE_OPENAI", "0").lower() in ("1", "true", "yes")

# company roles
companyRoles = [
    "Manager",
    "Chef",
    "Cook",
    "Waiter",
    "Bartender"
]

# Function to load data from CSV files
def load_data():
    # Ensure these files exist in your directory
    df_calendar = pd.read_csv('calendar.csv')
    df_team = pd.read_csv('team_availability.csv')
    return df_calendar, df_team

# This function is the core of the AI scheduling logic.
def get_ai_schedule(availability_data, requirements, roles_list):
    if not OPENAI_API_KEY or openai is None:
        return "AI Schedule Placeholder"

    client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

    # 1. Prepare the Data
    availability_markdown = availability_data[['Name', 'Default_Role', 'Shift_Start', 'Shift_End', 'Max_Hours']].to_markdown(index=False)

    # 2. Simplified Prompt - We only ask the AI for the ROLE.
    # We tell it we will handle the times ourselves to keep it from getting confused.
    prompt = f"""
    Assign exactly one role to each employee based on requirements.
    
    Requirements: {requirements}
    Allowed Roles: {roles_list}

    Output format: Name | Role
    
    Data:
    {availability_markdown}
    """

    try:
        response = client.chat.completions.create(
            model="llama3.2",
            messages=[{"role": "system", "content": "You are a helpful assistant that only outputs Name | Role."},
                      {"role": "user", "content": prompt}],
            temperature=0.1
        )
        ai_text = response.choices[0].message.content
        
        # 3. Create the Final Table
        table_lines = [
            "| Employee Name | Assigned Role | Shift Start | Shift End | Hours |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]

        # Parse AI roles into a dictionary
        role_assignments = {}
        for line in ai_text.strip().split("\n"):
            if "|" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2:
                    role_assignments[parts[0]] = parts[1]

        # 4. PYTHON LOGIC: Handle the 8-hour clipping
        for _, row in availability_data.sort_values(by="Name").iterrows():
            name = row['Name']
            role = role_assignments.get(name, row['Default_Role'])
            
            # Get raw start/end from CSV
            start_str = row['Shift_Start']
            max_hours = int(row['Max_Hours'])
            
            # --- THE CLIPPER ---
            # We take the start time and FORCE the end time to be Start + Max_Hours
            try:
                start_hour = int(start_str.split(':')[0])
                end_hour = start_hour + max_hours
                
                # Format back to HH:00 (e.g., 8 becomes 08:00, 16 becomes 16:00)
                final_start = f"{start_hour:02d}:00"
                final_end = f"{min(end_hour, 23):02d}:00" # Don't go past 11PM
            except:
                final_start = row['Shift_Start']
                final_end = row['Shift_End']

            table_lines.append(f"| {name} | {role} | {final_start} | {final_end} | {max_hours} |")

        return "\n".join(table_lines)

    except Exception as error:
        return f"Error: {error}"

   


# ================= MAIN FUNCTION =================
def main():
    # 1. Load Data
    calendar, team = load_data()

    # 2. Define today's necessity (This is your 'Changing roles' idea)
    # You could eventually automate this based on the date
    today_requirements = "We need 1 Chef, 2 Cooks, and 2 Waiters today."

    # 3. Get the schedule
    final_schedule = get_ai_schedule(team, today_requirements, companyRoles)

    # 4. Output
    print(final_schedule)


if __name__ == "__main__":
    main()
    