from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


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
        #Requesting Events
   
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 4 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=4, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

        event = {
                'summary': "Testing",
                'location': '800 Howard St., San Francisco, CA 94103',
                'description': "Testing Testing",
            'start': {
                    #'dateTime': 'YYYY-MM-DD:HH:MM:SS+05:30',
                    'dateTime': '2023-07-03T09:00:00+05:30',
                    'timeZone': 'Asia/Kolkata',
                },
            'end': {
                    'dateTime': '2023-07-03T11:00:00+05:30',
                    'timeZone': 'Asia/Kolkata',
                },
        }
        
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))


    except HttpError as error:
        print('An error occurred: %s' % error)



if __name__ == '__main__':
    main()

"""
from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    '''Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    '''
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
"""
