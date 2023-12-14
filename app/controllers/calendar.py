import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models.event import Event

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class Calendar:

    def __init__(self):
        self.__connect()

    def __connect(self):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            self.service = build("calendar", "v3", credentials=creds)
        except HttpError as error:
            print(f"An error occurred: {error}")

    def get_events(self, max_results=10):
        events_result = (self.service.events().list(
            calendarId="primary",
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute())
        events = events_result.get("items", [])
        return events

    def create_event(self, event):
        try:
            evt = Event(**event)
            event = self.service.events().insert(
                calendarId="primary", body=evt.__dict__).execute()
            print('Event created: %s' % (event.get('htmlLink')))
        except Exception as e:
            print("Error:", e)
