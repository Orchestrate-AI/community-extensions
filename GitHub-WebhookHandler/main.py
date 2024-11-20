import json
import os
import asyncio
import aioredis

async def process_message(message):
    try:
        payload = json.loads(message)
        if payload.get('action') == 'created':
            return ''
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON payload")
        return None
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        return None

async def main():
    redis = await aioredis.from_url(
        os.environ['REDIS_HOST_URL'],
        username=os.environ['REDIS_USERNAME'],
        password=os.environ['REDIS_PASSWORD']
    )

    channel_in = os.environ['REDIS_CHANNEL_IN']
    channel_out = os.environ['REDIS_CHANNEL_OUT']
    channel_ready = os.environ['REDIS_CHANNEL_READY']
    workflow_instance_id = os.environ['WORKFLOW_INSTANCE_ID']
    workflow_extension_id = os.environ['WORKFLOW_EXTENSION_ID']

    await redis.publish(channel_ready, '')

    pubsub = redis.pubsub()
    await pubsub.subscribe(channel_in)

    try:
        async for message in pubsub.listen():
            if message['type'] == 'message':
                result = await process_message(message['data'])
                output = {
                    'type': 'completed',
                    'workflowInstanceId': workflow_instance_id,
                    'workflowExtensionId': workflow_extension_id,
                    'output': result
                }
                await redis.publish(channel_out, json.dumps(output))
                break
    finally:
        await pubsub.unsubscribe(channel_in)
        await redis.close()

if __name__ == "__main__":
    asyncio.run(main())