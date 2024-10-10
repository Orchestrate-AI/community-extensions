import os
import json
import asyncio
import aiohttp
import redis.asyncio as redis
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
WORKFLOW_INSTANCE_ID = os.environ['WORKFLOW_INSTANCE_ID']
WORKFLOW_EXTENSION_ID = os.environ['WORKFLOW_EXTENSION_ID']
REDIS_HOST_URL = os.environ['REDIS_HOST_URL']
REDIS_USERNAME = os.environ['REDIS_USERNAME']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_CHANNEL_IN = os.environ['REDIS_CHANNEL_IN']
REDIS_CHANNEL_OUT = os.environ['REDIS_CHANNEL_OUT']
REDIS_CHANNEL_READY = os.environ['REDIS_CHANNEL_READY']

async def get_inventory_levels(session, shop_url, access_token):
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    url = f'https://{shop_url}/admin/api/2023-04/inventory_levels.json'
    inventory_levels = []

    while url:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                inventory_levels.extend(data['inventory_levels'])
                url = response.links.get('next', {}).get('url')
            elif response.status == 401:
                raise Exception("Authentication failed. Please check your access token.")
            elif response.status == 429:
                retry_after = int(response.headers.get('Retry-After', 5))
                logger.warning(f"Rate limit reached. Waiting for {retry_after} seconds.")
                await asyncio.sleep(retry_after)
            else:
                raise Exception(f"Failed to fetch inventory levels: HTTP {response.status}")

    return inventory_levels

async def process_message(message):
    try:
        inputs = json.loads(message)['inputs']
        shop_url = inputs.get('shop_url')
        access_token = inputs.get('access_token')

        if not shop_url or not access_token:
            raise ValueError("Missing required inputs: shop_url and access_token")

        async with aiohttp.ClientSession() as session:
            inventory_levels = await get_inventory_levels(session, shop_url, access_token)

        return {
            'inventory_levels': inventory_levels
        }
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return {
            'error': str(e)
        }

async def main():
    redis_client = redis.Redis.from_url(REDIS_HOST_URL, username=REDIS_USERNAME, password=REDIS_PASSWORD)
    pubsub = redis_client.pubsub()
    
    await pubsub.subscribe(REDIS_CHANNEL_IN)
    await redis_client.publish(REDIS_CHANNEL_READY, '')
    logger.info("Extension ready to receive messages")

    async for message in pubsub.listen():
        if message['type'] == 'message':
            logger.info("Received message, processing...")
            result = await process_message(message['data'])
            
            output = {
                'type': 'completed',
                'workflowInstanceId': WORKFLOW_INSTANCE_ID,
                'workflowExtensionId': WORKFLOW_EXTENSION_ID,
                'output': result
            }
            
            await redis_client.publish(REDIS_CHANNEL_OUT, json.dumps(output))
            logger.info("Message processed and result published")
            break

    await pubsub.unsubscribe(REDIS_CHANNEL_IN)
    await redis_client.close()
    logger.info("Extension shutting down")

if __name__ == '__main__':
    asyncio.run(main())