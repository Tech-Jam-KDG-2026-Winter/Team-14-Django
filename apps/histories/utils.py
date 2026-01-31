import os
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']

def get_google_fit_credentials():
    client_secrets_file = os.path.join(settings.BASE_DIR, 'credentials.json')
    token_file = os.path.join(settings.BASE_DIR, 'token.json')
    
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, 
                SCOPES
            )
            creds = flow.run_local_server(port=8080, access_type='offline')
        
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_google_fit_steps(target_date=None):
    creds = get_google_fit_credentials()
    service = build('fitness', 'v1', credentials=creds)
    if target_date is None:
        target_date = datetime.date.today()
    start_time = datetime.datetime.combine(target_date, datetime.time.min)
    end_time = datetime.datetime.combine(target_date, datetime.time.max)
    start_time_ms = int(start_time.timestamp() * 1000)
    end_time_ms = int(end_time.timestamp() * 1000)
    body = {
        "aggregateBy": [{"dataTypeName": "com.google.step_count.delta"}],
        "bucketByTime": { "durationMillis": 86400000 },
        "startTimeMillis": start_time_ms,
        "endTimeMillis": end_time_ms
    }
    dataset = service.users().dataset().aggregate(userId='me', body=body).execute()
    total_steps = 0
    for bucket in dataset.get('bucket', []):
        for dataset_item in bucket.get('dataset', []):
            for point in dataset_item.get('point', []):
                val = point['value'][0]
                total_steps += val.get('intVal', 0) + int(val.get('fpVal', 0))
    return total_steps
