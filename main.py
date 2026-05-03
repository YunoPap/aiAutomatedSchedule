import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

try:
    import openai  # You'll need to pip install openai if you want real AI output
except ImportError:
    openai = None

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)  # Explicitly load the .env in the project root
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_OPENAI = os.getenv("USE_OPENAI", "0").lower() in ("1", "true", "yes")

# company roles
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

def get_ai_schedule(availability_data, requirements, roles_list):
    availability_str = availability_data.to_string()

    # We use the standard openai package, but point it to Ollama!
    if openai is None:
        print("--- openai package not installed; using placeholder output ---")
        return "AI Schedule Placeholder: [Simulated Table]"

    # Point to the local Ollama server running on your machine
    client = openai.OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"  # Ollama doesn't care what this string is
    )

    prompt = f"""
    Based on the following team availability:
    {availability_str}

    Daily Requirements:
    {requirements}

    Allowed Roles: {', '.join(roles_list)}

    Rules:
    1. Assign roles ONLY from the 'Allowed Roles' list.
    2. No one exceeds their 'Max_Hours'.
    3. Return the result as a Markdown table.
    """

    print("--- Sending to Local AI (Ollama) ---")

    try:
        response = client.chat.completions.create(
            model="llama3.2",  # Tell it to use the model you just pulled
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as error:
        print(f"--- Ollama request failed: {error}; using placeholder output ---")
        return "AI Schedule Placeholder: [Simulated Table]"


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
    