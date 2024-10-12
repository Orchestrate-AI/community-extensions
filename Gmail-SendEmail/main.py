import os
import json
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import redis
import asyncio

# Environment variables
WORKFLOW_INSTANCE_ID = os.environ['WORKFLOW_INSTANCE_ID']
WORKFLOW_EXTENSION_ID = os.environ['WORKFLOW_EXTENSION_ID']
REDIS_HOST_URL = os.environ['REDIS_HOST_URL']
REDIS_USERNAME = os.environ['REDIS_USERNAME']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_CHANNEL_IN = os.environ['REDIS_CHANNEL_IN']
REDIS_CHANNEL_OUT = os.environ['REDIS_CHANNEL_OUT']
REDIS_CHANNEL_READY = os.environ['REDIS_CHANNEL_READY']

async def send_email(to, subject, body, credentials):
    creds = Credentials.from_authorized_user_info(json.loads(credentials))
    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    try:
        sent_message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        return {'message_id': sent_message['id']}
    except Exception as e:
        return {'error': str(e)}

async def process_message(message):
    data = json.loads(message)
    inputs = data['inputs']

    to = inputs.get('to')
    subject = inputs.get('subject')
    body = inputs.get('body')
    credentials = inputs.get('credentials')

    if not all([to, subject, body, credentials]):
        return {'error': 'Missing required inputs'}

    result = await send_email(to, subject, body, credentials)
    return result

async def main():
    redis_client = redis.Redis.from_url(REDIS_HOST_URL, username=REDIS_USERNAME, password=REDIS_PASSWORD)
    pubsub = redis_client.pubsub()

    await pubsub.subscribe(REDIS_CHANNEL_IN)

    # Signal that the extension is ready
    await redis_client.publish(REDIS_CHANNEL_READY, '')

    async for message in pubsub.listen():
        if message['type'] == 'message':
            result = await process_message(message['data'])

            output = {
                'type': 'completed' if 'error' not in result else 'failed',
                'workflowInstanceId': WORKFLOW_INSTANCE_ID,
                'workflowExtensionId': WORKFLOW_EXTENSION_ID,
                'output': result
            }
            await redis_client.publish(REDIS_CHANNEL_OUT, json.dumps(output))

            # Unsubscribe and quit after processing the message
            await pubsub.unsubscribe(REDIS_CHANNEL_IN)
            break

    await redis_client.close()

if __name__ == '__main__':
    asyncio.run(main())