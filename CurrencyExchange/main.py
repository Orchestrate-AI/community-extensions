import os
import json
import asyncio
import aiohttp
from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()

WORKFLOW_INSTANCE_ID = os.getenv('WORKFLOW_INSTANCE_ID')
WORKFLOW_EXTENSION_ID = os.getenv('WORKFLOW_EXTENSION_ID')
REDIS_HOST_URL = os.getenv('REDIS_HOST_URL')
REDIS_USERNAME = os.getenv('REDIS_USERNAME')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_CHANNEL_IN = os.getenv('REDIS_CHANNEL_IN')
REDIS_CHANNEL_OUT = os.getenv('REDIS_CHANNEL_OUT')
REDIS_CHANNEL_READY = os.getenv('REDIS_CHANNEL_READY')

async def fetch_exchange_rates(app_id, base_currency, target_currencies):
    url = f"https://openexchangerates.org/api/latest.json?app_id={app_id}&base={base_currency}&symbols={target_currencies}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                raise Exception(f"API request failed with status {response.status}")

async def process_message(message):
    data = json.loads(message)
    inputs = data.get('inputs', {})
    
    app_id = inputs.get('app_id')
    base_currency = inputs.get('base_currency', 'USD')  # Default to USD as it's the only base currency allowed in the free tier
    target_currencies = inputs.get('target_currencies')
    
    if not app_id or not target_currencies:
        raise ValueError("'app_id' and 'target_currencies' are required in the input")
    
    target_currencies_list = [currency.strip() for currency in target_currencies.split(',')]
    target_currencies_str = ','.join(target_currencies_list)
    
    exchange_data = await fetch_exchange_rates(app_id, base_currency, target_currencies_str)
    
    return {
        "base_currency": exchange_data['base'],
        "date": exchange_data['timestamp'],
        "rates": {currency: rate for currency, rate in exchange_data['rates'].items() if currency in target_currencies_list}
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