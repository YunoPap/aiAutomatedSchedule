# SmartShift AI: Intelligent Staff Scheduler

SmartShift AI is an interactive scheduling application that automates team role assignments based on dynamic daily business demands, employee availability, and local AI optimization.

Developed in Python, the system utilizes **Streamlit** for the frontend dashboard, **Pandas** for managing the data files, and **Ollama** to run an open-source Large Language Model (LLM) entirely on the host machine.

---

## 🛠️ Project Architecture
                  +-----------------------------+
                  |     Streamlit Frontend      |
                  |          (app.py)           |
                  +--------------+--------------+
                                 |
                                 v
                  +-----------------------------+
                  |     Core Business Logic     |
                  |          (main.py)          |
                  +-------+--------------+------+
                          |              |
                          v              v

+-------------------------------+  +--------------------------------+
|          Data Layer           |  |          Local AI Engine       |
| (calendar.csv, availability)  |  |   (Ollama with Llama 3.2 3B)   |
+-------------------------------+  +--------------------------------+


---

## 📋 Features

- **Automated Scheduling:** Reads availability from `team_availability.csv` and cross-references it against requirements stored in `calendar.csv`.
- **Dynamic Data Management:** Sidebar forms allow users to immediately add new staff members and calendar events, modifying the CSV files on the fly.
- **Local LLM Integration:** Processes data securely using Ollama (`llama3.2`), bypassing the need for third-party API keys or internet dependencies.

---

## 🚀 Installation & Setup

Please follow these steps to install and run the application on your computer:

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system. 

You will also need to install **Ollama**, an engine for running LLMs locally.
- **macOS/Linux:** Open a terminal and run:
  ```bash
  curl -fsSL [https://ollama.com/install.sh](https://ollama.com/install.sh) | sh

  2. Download the AI Model

Once Ollama is installed and running in the background, pull the lightweight 3-billion parameter model required for this project:
Bash

ollama pull llama3.2

3. Navigate to the Project Folder

Open your terminal inside the project directory:
Bash

cd pythonFinalProject

4. Install Python Dependencies

Install the required packages using the bundled requirements.txt file. We recommend creating a virtual environment:
Bash

python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt

🖥️ How to Run the App

With your virtual environment active and Ollama running in the background, launch the Streamlit frontend:
Bash

streamlit run app.py

Your web browser should automatically open the dashboard at http://localhost:8501.