import os
import json
import asyncio
import aiohttp
import aioredis

SHOPIFY_SHOP_NAME = 'your-shop-name'  # This should be provided in the input
SHOPIFY_ACCESS_TOKEN = 'your-access-token'  # This should be provided in the input
API_VERSION = '2023-04'

async def get_product_variants(session, product_id):
    url = f"https://{SHOPIFY_SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products/{product_id}/variants.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            return [variant['inventory_item_id'] for variant in data['variants']]
        else:
            return []

async def get_inventory_levels(session, inventory_item_ids):
    url = f"https://{SHOPIFY_SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/inventory_levels.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    params = {
        "inventory_item_ids": ",".join(map(str, inventory_item_ids))
    }
    async with session.get(url, headers=headers, params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            return {"inventory_levels": []}

async def process_message(message):
    try:
        data = json.loads(message)
        product_ids = data['inputs'].get('product_ids', [])
        
        async with aiohttp.ClientSession() as session:
            all_inventory_item_ids = []
            for product_id in product_ids:
                inventory_item_ids = await get_product_variants(session, product_id)
                all_inventory_item_ids.extend(inventory_item_ids)
            
            inventory_levels = await get_inventory_levels(session, all_inventory_item_ids)
        
        return {
            "inventory_levels": inventory_levels['inventory_levels']
        }
    except Exception as e:
        return {
            "error": str(e)
        }

async def main():
    redis = await aioredis.create_redis_pool(os.environ['REDIS_HOST_URL'], username=os.environ['REDIS_USERNAME'], password=os.environ['REDIS_PASSWORD'])

    channel_in = os.environ['REDIS_CHANNEL_IN']
    channel_out = os.environ['REDIS_CHANNEL_OUT']
    channel_ready = os.environ['REDIS_CHANNEL_READY']

    await redis.publish(channel_ready, '')

    try:
        while True:
            message = await redis.subscribe(channel_in)
            result = await process_message(message)

            output = {
                "type": "completed",
                "workflowInstanceId": os.environ['WORKFLOW_INSTANCE_ID'],
                "workflowExtensionId": os.environ['WORKFLOW_EXTENSION_ID'],
                "output": result
            }
            await redis.publish(channel_out, json.dumps(output))
    except Exception as e:
        error_output = {
            "type": "failed",
            "workflowInstanceId": os.environ['WORKFLOW_INSTANCE_ID'],
            "workflowExtensionId": os.environ['WORKFLOW_EXTENSION_ID'],
            "error": str(e)
        }
        await redis.publish(channel_out, json.dumps(error_output))
    finally:
        redis.close()
        await redis.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())