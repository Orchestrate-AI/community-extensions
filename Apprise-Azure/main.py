import os
import json
import asyncio
from redis.asyncio import Redis
from dotenv import load_dotenv
import apprise
from azure.communication.sms import SmsClient
from azure.communication.email import EmailClient
from azure.core.exceptions import AzureError

load_dotenv()

WORKFLOW_ID = os.getenv('WORKFLOW_ID')
WORKFLOW_INSTANCE_ID = os.getenv('WORKFLOW_INSTANCE_ID')
WORKFLOW_EXTENSION_ID = os.getenv('WORKFLOW_EXTENSION_ID')
REDIS_HOST_URL = os.getenv('REDIS_HOST_URL')
REDIS_USERNAME = os.getenv('REDIS_USERNAME')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_CHANNEL_IN = os.getenv('REDIS_CHANNEL_IN')
REDIS_CHANNEL_OUT = os.getenv('REDIS_CHANNEL_OUT')
REDIS_CHANNEL_READY = os.getenv('REDIS_CHANNEL_READY')

def send_azure_sms(connection_string, from_phone_number, to_phone_number, title, body):
    try:
        sms_client = SmsClient.from_connection_string(connection_string)
        response = sms_client.send(
            from_=from_phone_number,
            to=to_phone_number,
            message=f"{title}\n\n{body}"
        )
        return response.successful
    except AzureError as e:
        print(f"An error occurred: {e}")
        return False

def send_azure_email(connection_string, sender_address, to_email, title, body):
    try:
        email_client = EmailClient.from_connection_string(connection_string)
        message = {
            "content": {
                "subject": title,
                "plainText": body,
            },
            "recipients": {
                "to": [{"address": to_email}],
            },
            "senderAddress": sender_address
        }
        poller = email_client.begin_send(message)
        result = poller.result()
        return result is not None and hasattr(result, 'message_id')
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

async def process_message(message):
    data = json.loads(message)
    inputs = data.get('inputs', {})
    notification_url = inputs.get('notificationUrl')
    title = inputs.get('title')
    body = inputs.get('body')
    azure_connection_string = inputs.get('azureConnectionString')
    azure_phone_number = inputs.get('azurePhoneNumber')
    azure_email_sender = inputs.get('azureEmailSender')
    
    if not notification_url or not title or not body:
        raise ValueError("'notificationUrl', 'title', and 'body' are required in the input")

    # Create an Apprise instance
    apobj = apprise.Apprise()

    # Handle Azure services
    if notification_url.startswith('azuresms://'):
        if not azure_connection_string or not azure_phone_number:
            raise ValueError("'azureConnectionString' and 'azurePhoneNumber' are required for Azure SMS")
        to_phone_number = notification_url.split('/')[-1]
        result = send_azure_sms(azure_connection_string, azure_phone_number, to_phone_number, title, body)
    elif notification_url.startswith('azureemail://'):
        if not azure_connection_string or not azure_email_sender:
            raise ValueError("'azureConnectionString' and 'azureEmailSender' are required for Azure Email")
        to_email = notification_url.split('/')[-1]
        result = send_azure_email(azure_connection_string, azure_email_sender, to_email, title, body)
    else:
        # Use standard Apprise notification for other URLs
        apobj.add(notification_url)
        result = apobj.notify(body=body, title=title)

    return {
        "success": result,
        "notification_url": notification_url,
        "title": title,
        "body": body
    }

async def main():
    redis = Redis.from_url(
        REDIS_HOST_URL,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD
    )

    await redis.publish(REDIS_CHANNEL_READY, '')

    pubsub = redis.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL_IN)

    async for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                result = await process_message(message['data'])
                output = {
                    "type": "completed",
                    "workflowId": WORKFLOW_ID,
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "output": result
                }
            except Exception as e:
                output = {
                    "type": "failed",
                    "workflowId": WORKFLOW_ID,
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "error": str(e)
                }
            
            await redis.publish(REDIS_CHANNEL_OUT, json.dumps(output))
            await redis.close()
            break

    await pubsub.unsubscribe(REDIS_CHANNEL_IN)
    await redis.close()

if __name__ == "__main__":
    asyncio.run(main())