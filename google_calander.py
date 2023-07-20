from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_creds():
    # File
    file = "credentials.json"

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def add_event(
    id, start_date, start_time, end_date, end_time, summary, location, description
):
    creds = get_creds()
    service = build("calendar", "v3", credentials=creds)
    event = {
        "id": id,
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
            "dateTime": start_date + "T" + start_time + "+05:30",
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_date + "T" + end_time + "+05:30",
            "timeZone": "Asia/Kolkata",
        },
    }
    event = service.events().insert(calendarId="primary", body=event).execute()
    return "Event created: %s" % (event.get("htmlLink"))


def delete_event(id):
    creds = get_creds()
    service = build("calendar", "v3", credentials=creds)
    try:
        service.events().delete(calendarId="primary", eventId=id).execute()
        return "Event deleted"
    except HttpError as error:
        return error


# print(add_event(id="2023070419", start_date="2023-07-04", start_time="11:00:00", end_date="2023-07-04", end_time="13:00:00", summary="test&test", location="hogwards", description="timepassispasstime"))
# print(delete_event("2023070419"))

'''
def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    try:
        service = build('calendar', 'v3', credentials=creds)
        event = {
                'id': '34567',
                'summary': "Testing23456",
                'location': '800 Howard St., San Francisco, CA 94103',
                'description': "Testing Testing",
            'start': {
                    #'dateTime': 'YYYY-MM-DD:HH:MM:SS+05:30',
                    'dateTime': '2023-07-03T19:00:00+05:30',
                    'timeZone': 'Asia/Kolkata',
                },
            'end': {
                    'dateTime': '2023-07-03T21:00:00+05:30',
                    'timeZone': 'Asia/Kolkata',
                },
        }
        
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))

        event_id = "23456"

        # Delete each event
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print(f"Event with ID {event_id} deleted successfully.")


    except HttpError as error:
        print('An error occurred: %s' % error)



if __name__ == '__main__':
    main()
'''
