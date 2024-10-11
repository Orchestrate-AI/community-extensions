import os
import json
import asyncio
from redis.asyncio import Redis
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

WORKFLOW_INSTANCE_ID = os.getenv('WORKFLOW_INSTANCE_ID')
WORKFLOW_EXTENSION_ID = os.getenv('WORKFLOW_EXTENSION_ID')
REDIS_HOST_URL = os.getenv('REDIS_HOST_URL')
REDIS_USERNAME = os.getenv('REDIS_USERNAME')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_CHANNEL_IN = os.getenv('REDIS_CHANNEL_IN')
REDIS_CHANNEL_OUT = os.getenv('REDIS_CHANNEL_OUT')
REDIS_CHANNEL_READY = os.getenv('REDIS_CHANNEL_READY')

def connect_to_redis():

    return Redis.from_url(
        REDIS_HOST_URL,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

def scrape_zillow(zipcode, min_price, max_price):
    url = f"https://www.zillow.com/homes/{zipcode}_rb/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    params = {
        'searchQueryState': json.dumps({
            "pagination": {},
            "usersSearchTerm": zipcode,
            "mapBounds": {"west": -180, "east": 180, "south": -90, "north": 90},
            "regionSelection": [{"regionId": 0, "regionType": 7}],
            "isMapVisible": False,
            "filterState": {
                "price": {"min": min_price, "max": max_price},
                "mp": {"min": min_price, "max": max_price},
                "sort": {"value": "globalrelevanceex"},
                "ah": {"value": True}
            },
            "isListVisible": True
        })
    }

    response = requests.get(url, headers=headers, params=params)
    soup = BeautifulSoup(response.content, 'html.parser')

    listings = []
    for item in soup.select('.list-card'):
        try:
            listing = {
                'address': item.select_one('.list-card-addr').text,
                'price': item.select_one('.list-card-price').text,
                'details': item.select_one('.list-card-details').text,
                'link': item['href'] if item.has_attr('href') else ''
            }
            listings.append(listing)
        except AttributeError:
            continue

    return listings

async def process_message(message):
    data = json.loads(message)
    inputs = data['inputs']
    zipcode = inputs['zipcode']
    min_price = inputs['min_price']
    max_price = inputs['max_price']

    listings = scrape_zillow(zipcode, min_price, max_price)

    return {
        'listings': listings,
        'count': len(listings)
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
