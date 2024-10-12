import os
import json
import redis
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Environment variables
REDIS_HOST_URL = os.environ['REDIS_HOST_URL']
REDIS_USERNAME = os.environ['REDIS_USERNAME']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_CHANNEL_IN = os.environ['REDIS_CHANNEL_IN']
REDIS_CHANNEL_OUT = os.environ['REDIS_CHANNEL_OUT']
REDIS_CHANNEL_READY = os.environ['REDIS_CHANNEL_READY']
WORKFLOW_INSTANCE_ID = os.environ['WORKFLOW_INSTANCE_ID']
WORKFLOW_EXTENSION_ID = os.environ['WORKFLOW_EXTENSION_ID']

# Initialize Redis clients
redis_client = redis.Redis(host=REDIS_HOST_URL, username=REDIS_USERNAME, password=REDIS_PASSWORD, decode_responses=True)
pubsub = redis_client.pubsub()

def create_calendar_event(credentials, event_details):
    service = build('calendar', 'v3', credentials=credentials)
    event = service.events().insert(calendarId='primary', body=event_details).execute()
    return event['id']

def process_message(message):
    try:
        data = json.loads(message['data'])
        inputs = data['inputs']
        
        # Extract event details from inputs
        event_details = {
            'summary': inputs['summary'],
            'location': inputs.get('location', ''),
            'description': inputs.get('description', ''),
            'start': {
                'dateTime': inputs['start_time'],
                'timeZone': inputs.get('time_zone', 'UTC'),
            },
            'end': {
                'dateTime': inputs['end_time'],
                'timeZone': inputs.get('time_zone', 'UTC'),
            },
        }
        
        # Create credentials object
        credentials = Credentials.from_authorized_user_info(json.loads(inputs['google_credentials']))
        
        # Refresh token if expired
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        
        # Create calendar event
        event_id = create_calendar_event(credentials, event_details)
        
        return {'status': 'success', 'event_id': event_id}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def main():
    pubsub.subscribe(REDIS_CHANNEL_IN)
    redis_client.publish(REDIS_CHANNEL_READY, '')
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            result = process_message(message)
            
            output = {
                'type': 'completed' if result['status'] == 'success' else 'failed',
                'workflowInstanceId': WORKFLOW_INSTANCE_ID,
                'workflowExtensionId': WORKFLOW_EXTENSION_ID,
                'output': result
            }
            
            redis_client.publish(REDIS_CHANNEL_OUT, json.dumps(output))
            break
    
    pubsub.unsubscribe(REDIS_CHANNEL_IN)
    redis_client.close()

if __name__ == '__main__':
    main()