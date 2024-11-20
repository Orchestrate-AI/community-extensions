import os
import json
import redis
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

# Environment variables
WORKFLOW_INSTANCE_ID = os.environ['WORKFLOW_INSTANCE_ID']
WORKFLOW_EXTENSION_ID = os.environ['WORKFLOW_EXTENSION_ID']
REDIS_HOST_URL = os.environ['REDIS_HOST_URL']
REDIS_USERNAME = os.environ['REDIS_USERNAME']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_CHANNEL_IN = os.environ['REDIS_CHANNEL_IN']
REDIS_CHANNEL_OUT = os.environ['REDIS_CHANNEL_OUT']
REDIS_CHANNEL_READY = os.environ['REDIS_CHANNEL_READY']

# Initialize Redis clients
publisher = redis.Redis.from_url(
    REDIS_HOST_URL,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD
)
subscriber = redis.Redis.from_url(
    REDIS_HOST_URL,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD
)

# Initialize MailChimp client
mailchimp = MailchimpMarketing.Client()

def add_subscriber(api_key, server_prefix, list_id, email, additional_fields=None):
    mailchimp.set_config({
        "api_key": api_key,
        "server": server_prefix
    })

    member_info = {
        "email_address": email,
        "status": "subscribed"
    }

    if additional_fields:
        member_info.update(additional_fields)

    try:
        response = mailchimp.lists.add_list_member(list_id, member_info)
        return {
            "success": True,
            "message": f"Contact {email} added successfully",
            "id": response["id"]
        }
    except ApiClientError as error:
        return {
            "success": False,
            "message": f"An error occurred: {error.text}"
        }

def process_message(message):
    try:
        data = json.loads(message)
        inputs = data['inputs']

        api_key = inputs['api_key']
        server_prefix = inputs['server_prefix']
        list_id = inputs['list_id']
        email = inputs['email']
        additional_fields = inputs.get('additional_fields', {})

        result = add_subscriber(api_key, server_prefix, list_id, email, additional_fields)
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing message: {str(e)}"
        }

async def main():
    await publisher.publish(REDIS_CHANNEL_READY, '')

    pubsub = subscriber.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL_IN)

    async for message in pubsub.listen():
        if message['type'] == 'message':
            result = process_message(message['data'])

            output = {
                "type": "completed" if result["success"] else "failed",
                "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                "output": result
            }
            await publisher.publish(REDIS_CHANNEL_OUT, json.dumps(output))

            await pubsub.unsubscribe(REDIS_CHANNEL_IN)
            break

    await publisher.close()
    await subscriber.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())