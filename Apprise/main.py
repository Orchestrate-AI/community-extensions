import os
import json
import asyncio
from redis.asyncio import Redis
from dotenv import load_dotenv
import apprise

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

async def process_message(message):
    data = json.loads(message)
    inputs = data.get('inputs', {})
    notification_url = inputs.get('notificationUrl')
    title = inputs.get('title')
    body = inputs.get('body')
    
    if not notification_url or not title or not body:
        raise ValueError("'notificationUrl', 'title', and 'body' are required in the input")

    # Create an Apprise instance
    apobj = apprise.Apprise()

    # Add the notification service
    apobj.add(notification_url)

    # Send the notification
    result = apobj.notify(
        body=body,
        title=title
    )

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