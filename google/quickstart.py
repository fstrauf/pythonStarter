from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import random

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': 'FLOW Survey',
        'location': 'Google Form',      
        'description': 'https://docs.google.com/forms/d/e/1FAIpQLSf0ctH6MTM-rCRKBJ4DFjzHP6mhqYc2W8x2tjC31XycBGam-Q/viewform?usp=sf_link',  
        'start': {
            'dateTime': '2020-04-22T16:51:29.502413',
            'timeZone': 'Australia/Sydney'
        },
        'end': {
            'dateTime': '2020-04-22T16:51:29.502413',
            'timeZone': 'Australia/Sydney'
        },
        'reminders': {
            'useDefault': True            
        },
    }
    
    for i in range(7):
        now = datetime.datetime.now()
        day = now + datetime.timedelta(days=i+1)
        for x in range(6): 
            start = day.replace(hour=random.randint(6,19),minute=random.randint(0,59))
            end = start + datetime.timedelta(minutes=5)
            event['start']['dateTime']=start.isoformat()
            event['end']['dateTime']=end.isoformat()
            service.events().insert(calendarId='primary', body=event).execute()
            print (event.get('htmlLink'))

if __name__ == '__main__':
    main()