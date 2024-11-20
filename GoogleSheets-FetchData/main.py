import os
import json
import redis
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Redis connection setup
redis_client = redis.Redis(
    host=os.environ['REDIS_HOST_URL'],
    username=os.environ['REDIS_USERNAME'],
    password=os.environ['REDIS_PASSWORD']
)

def process_message(message):
    inputs = json.loads(message)['inputs']
    
    # Extract inputs
    spreadsheet_id = inputs['spreadsheet_id']
    range_name = inputs['range_name']
    credentials_json = json.loads(inputs['credentials_json'])

    # Set up credentials
    creds = service_account.Credentials.from_service_account_info(
        credentials_json,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )

    # Build the Google Sheets service
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    return {
        'data': values
    }

def main():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(os.environ['REDIS_CHANNEL_IN'])

    # Signal that the extension is ready
    redis_client.publish(os.environ['REDIS_CHANNEL_READY'], '')

    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                result = process_message(message['data'].decode('utf-8'))
                output = {
                    'type': 'completed',
                    'workflowInstanceId': os.environ['WORKFLOW_INSTANCE_ID'],
                    'workflowExtensionId': os.environ['WORKFLOW_EXTENSION_ID'],
                    'output': result
                }
                redis_client.publish(os.environ['REDIS_CHANNEL_OUT'], json.dumps(output))
            except Exception as e:
                error_output = {
                    'type': 'failed',
                    'workflowInstanceId': os.environ['WORKFLOW_INSTANCE_ID'],
                    'workflowExtensionId': os.environ['WORKFLOW_EXTENSION_ID'],
                    'error': str(e)
                }
                redis_client.publish(os.environ['REDIS_CHANNEL_OUT'], json.dumps(error_output))
            finally:
                pubsub.unsubscribe(os.environ['REDIS_CHANNEL_IN'])
                redis_client.close()
                break

if __name__ == '__main__':
    main()