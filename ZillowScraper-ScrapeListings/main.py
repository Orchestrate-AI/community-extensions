import os
import json
import redis
import requests
from bs4 import BeautifulSoup

def connect_to_redis():

    return Redis.from_url(
        os.environ['REDIS_HOST_URL'],
        username=os.environ['REDIS_USERNAME'],
        password=os.environ['REDIS_PASSWORD'],
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

def process_message(message):
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

def main():
    redis_client = connect_to_redis()
    pubsub = redis_client.pubsub()

    pubsub.subscribe(os.environ['REDIS_CHANNEL_IN'])
    redis_client.publish(os.environ['REDIS_CHANNEL_READY'], '')

    for message in pubsub.listen():
        if message['type'] == 'message':
            result = process_message(message['data'])

            output = {
                'type': 'completed',
                'workflowInstanceId': os.environ['WORKFLOW_INSTANCE_ID'],
                'workflowExtensionId': os.environ['WORKFLOW_EXTENSION_ID'],
                'output': result
            }
            redis_client.publish(os.environ['REDIS_CHANNEL_OUT'], json.dumps(output))

            pubsub.unsubscribe(os.environ['REDIS_CHANNEL_IN'])
            break

    redis_client.close()

if __name__ == "__main__":
    main()