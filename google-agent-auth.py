from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from typing import Optional
import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_calendar_service() -> Optional[any]:
    """Authenticate and return a Google Calendar service object."""
    
    creds = None
    
    try:
        with open('token.pickle', 'rb') as token:
            creds = Credentials.from_pickle(token.read())
    except FileNotFoundError:
        pass
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('.credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            token.write(creds.to_pickle())
    
    if creds:
        return build('calendar', 'v3', credentials=creds)
    return None

def main():
    service = get_google_calendar_service()
    
    if service:
        # List the next 10 events from the user's calendar
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
        
        # Create a new event
        event = {
            'summary': 'New Event',
            'location': 'My Home',
            'description': 'A new event created via API.',
            'start': {
                'dateTime': '2023-11-25T09:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': '2023-11-25T10:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            },
        }
        
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f'Event created: {event.get("htmlLink")}')
    else:
        print("Could not authenticate.")

if __name__ == '__main__':
    main()
