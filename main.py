import os
import pandas as pd
from dotenv import load_dotenv
# import openai  # You'll need to pip install openai

load_dotenv()  # Loads your OPENAI_API_KEY from .env or the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#company roles
companyRoles = [
    "Chef",
    "Cook",
    "Waiter",
    "Manager",
    "Dishwasher"
]

def load_data():
    # Ensure these files exist in your directory
    df_calendar = pd.read_csv('calendar.csv')
    df_team = pd.read_csv('team_availability.csv')
    return df_calendar, df_team

def get_ai_schedule(availability_data, requirements):
    # Convert dataframe to string/json so the AI can process it
    availability_str = availability_data.to_string()
    
    prompt = f"""
    Based on the following team availability:
    {availability_str}
    
    Daily Requirements:
    {requirements}
    
    Rules:
    1. Assign roles based on the 'companyRoles' list.
    2. No one exceeds 8 hours.
    3. Ensure every role in 'requirements' is filled.
    
    Return the result as a Markdown table.
    """
    
    print("--- Sending to AI ---")
    # Example call (Uncomment when you have your API key set up)
    # response = openai.chat.completions.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": prompt}]
    # )
    # return response.choices[0].message.content
    return "AI Schedule Placeholder: [Simulated Table]"

def main():
    # 0. Validate environment
    if not OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY is not set. AI call will use placeholder output.")

    # 1. Load Data
    calendar, team = load_data()
    
    # 2. Define today's necessity (This is your 'Changing roles' idea)
    # You could eventually automate this based on the date
    today_requirements = "We need 1 Chef, 2 Cooks, and 2 Waiters today."
    
    # 3. Get the schedule
    final_schedule = get_ai_schedule(team, today_requirements)
    
    # 4. Output
    print(final_schedule)

if __name__ == "__main__":
    main()
    