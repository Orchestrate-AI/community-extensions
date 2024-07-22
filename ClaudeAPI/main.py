import os
import json
import asyncio
from redis.asyncio import Redis
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

load_dotenv()

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
    prompt = inputs.get('prompt')
    system_prompt = inputs.get('systemPrompt')
    api_key = inputs.get('anthropicAPIKey')

    if not prompt or not system_prompt or not api_key:
        raise ValueError("'prompt', 'system_prompt', and 'anthropic_api_key' are required in the input")

    client = AsyncAnthropic(api_key=api_key)

    try:
        response = await client.messages.create(
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ],
            system = system_prompt,
            model="claude-3-5-sonnet-20240620",
        )

        return {
            "claudeResponse": response.content[0].text,
            "prompt": prompt,
            "system_prompt": system_prompt,
            "model": response.model
        }
    finally:
        await client.close()

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
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "output": result
                }
            except Exception as e:
                output = {
                    "type": "failed",
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