import datetime
import os.path
import pytz  # Library for timezone handling

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
# This scope allows full access to the calendar, which is needed to create events.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authenticate_google_calendar():
    """
    Authenticates with the Google Calendar API.
    Checks for an existing token.json, refreshes it if expired,
    or performs a new authentication flow if no token exists.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This initiates a web-based authentication flow.
            # A browser window will open for the user to sign into their Google account and grant permissions to the app.
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def create_calendar_event(
    service,
    client_email,
    event_summary,
    event_description,
    start_datetime_str,
    end_datetime_str,
    timezone="Asia/Jerusalem"  # Default timezone, can be changed.
):
    """
    Creates a Google Calendar event and invites a client with view-only access.
    Args:
        service: The Google Calendar API service object.
        client_email (str): The email address of the client to invite.
        event_summary (str): The title of the event.
        event_description (str): A detailed description of the event.
        start_datetime_str (str): Start date and time in "YYYY-MM-DD HH:MM" format.
        end_datetime_str (str): End date and time in "YYYY-MM-DD HH:MM" format.
        timezone (str): The timezone for the event (e.g., "America/New_York", "Europe/London").
                        Valid timezones can be found here: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        reference: https://developers.google.com/workspace/calendar/api/v3/reference/events
    """
    try:
        # Parse datetime strings and localize to the specified timezone.
        local_tz = pytz.timezone(timezone)
        start_dt = local_tz.localize(datetime.datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M"))
        end_dt = local_tz.localize(datetime.datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M"))

        event = {
            'summary': event_summary,
            'description': event_description,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': timezone,
            },
            'attendees': [
                {'email': client_email},
            ],
            # Key settings for client permissions:
            'guestsCanModify': False,       # Client cannot modify the event.
            'guestsCanInviteOthers': False, # Client cannot invite others.
            'guestsCanSeeOtherGuests': False, # Client cannot see other invited guests.
            'conferenceData': { # Optional: To add a Google Meet link
                'createRequest': {
                    'requestId': f"meeting-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 24 hours before
                    {'method': 'popup', 'minutes': 10},      # 10 minutes before
                ],
            },
        }

        # Insert the event into the primary calendar.
        event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
        print(f"Event created: {event.get('htmlLink')}")
        print(f"Client '{client_email}' successfully invited.")

    except HttpError as error:
        print(f"An HTTP error occurred: {error}")
        print("Please ensure the client email is valid and you have granted the necessary permissions.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """
    Main function to run the scheduling application.
    """
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)

    print("\n--- Google Calendar Client Scheduler ---")
    print("Enter event details. Type 'done' for client email to quit.")

    while True:
        client_email = input("\nEnter client email (type 'done' to quit): ").strip()
        if client_email.lower() == 'done':
            break

        event_summary = input("Enter event summary (e.g., 'Consultation with [Client Name]'): ").strip()
        event_description = input("Enter event description (e.g., 'Discuss project proposal'): ").strip()

        # Example: 2025-07-31 10:00
        start_datetime_str = input("Enter start date and time (YYYY-MM-DD HH:MM, e.g., 2025-08-15 14:00): ").strip()
        end_datetime_str = input("Enter end date and time (YYYY-MM-DD HH:MM, e.g., 2025-08-15 15:00): ").strip()

        # IMPORTANT: Set your local timezone here.
        # Valid timezones can be found at https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        # Examples: "America/New_York", "Europe/London", "Asia/Tokyo", "Asia/Kolkata", "Asia/Jerusalem"
        event_timezone = input("Enter event timezone (default: Asia/Jerusalem): ").strip()
        if not event_timezone:
            event_timezone = "Asia/Jerusalem"  # Default to Jerusalem if not provided

        create_calendar_event(
            service,
            client_email,
            event_summary,
            event_description,
            start_datetime_str,
            end_datetime_str,
            event_timezone
        )

    print("\nEvent creation complete. Exiting.")

if __name__ == "__main__":
    main()
