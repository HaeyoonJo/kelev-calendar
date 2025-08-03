# Google Calendar Client Scheduler

This project provides a Python script to automate the scheduling of Google Calendar events by reading event details from a CSV file. It leverages the Google Calendar API to create events and invite clients with specific permissions.

-----

## Setup and Installation

Follow these steps to set up and run the Google Calendar Client Scheduler.

### 1\. Clone the Repository (if applicable)

If your code is in a repository, start by cloning it:

```bash
git clone <repository-url>
cd <repository-name>
```

Otherwise, navigate to the directory containing your Python script (`schedule_from_csv.py`) and your `credentials.json` file.

### 2\. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies. This isolates your project's packages from your system's global Python installation.

```bash
python3 -m venv venv
```

### 3\. Activate the Virtual Environment

Before installing dependencies or running the script, activate the virtual environment:

  * **On macOS and Linux:**

    ```bash
    source venv/bin/activate
    ```

  * **On Windows (Command Prompt):**

    ```cmd
    venv\Scripts\activate.bat
    ```

  * **On Windows (PowerShell):**

    ```powershell
    venv\Scripts\Activate.ps1
    ```

    Your terminal prompt should change (e.g., `(venv) your_username@your_machine:~/your_project$`), indicating the virtual environment is active.

### 4\. Install Dependencies

Install the required Python libraries using `pip`. First, create a `requirements.txt` file in your project directory with the following content:

```
google-api-python-client
google-auth-oauthlib
pytz
```

Then, install them:

```bash
pip install -r requirements.txt
```

### 5\. Google Calendar API Credentials

You need a `credentials.json` file from Google Cloud Platform to authenticate with the Google Calendar API.

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project or select an existing one.
3.  Navigate to "APIs & Services" \> "Enabled APIs & Services" and ensure "Google Calendar API" is enabled.
4.  Go to "APIs & Services" \> "Credentials".
5.  Click "CREATE CREDENTIALS" \> "OAuth client ID".
6.  Choose "Desktop app" as the application type and create it.
7.  Download the `credentials.json` file and place it in the same directory as your Python script.

The first time you run the script, a web browser will open, prompting you to log in to your Google account and grant permissions to the application. After successful authentication, a `token.json` file will be created to store your credentials for future use.

-----

## Usage

### Prepare Your CSV File

Create a CSV file (e.g., `events.csv`) with the following header row and event details. Ensure the column names match exactly as shown, including capitalization.

```csv
Client Email,Summary,Description,Start Time,End Time,Timezone
client1@example.com,Project Kick-off,Discuss initial project requirements,2025-08-10 09:00,2025-08-10 10:00,America/New_York
client2@example.com,Follow-up Meeting,Review progress on marketing campaign,2025-08-11 14:30,2025-08-11 15:00,Europe/London
client3@example.com,Consultation,Deep dive into technical architecture,2025-08-12 11:00,2025-08-12 12:00,Asia/Jerusalem
client4@example.com,Quick Sync,Check-in on design mockups,2025-08-13 16:00,2025-08-13 16:15,Asia/Kolkata
```

  * **Date/Time Format**: Ensure `Start Time` and `End Time` columns are in `YYYY-MM-DD HH:MM` format.
  * **Timezone**: Use valid [tz database time zone names](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). If this field is left empty in a row, the event will default to `Asia/Jerusalem`.

### Run the Script

Once your virtual environment is active, your dependencies are installed, and your `credentials.json` and CSV file are ready, run the script:

```bash
python schedule_from_csv.py
```

The script will prompt you to enter the path to your CSV file (e.g., `events.csv`). It will then process each row, creating a Google Calendar event and inviting the specified client.

-----

## Deactivate Virtual Environment

When you're done using the script, you can deactivate the virtual environment:

```bash
deactivate
```

This returns your terminal to its normal state.