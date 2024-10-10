import os
import json
import redis
import requests
from typing import Dict, Any

# Environment variables
WORKFLOW_INSTANCE_ID = os.environ['WORKFLOW_INSTANCE_ID']
WORKFLOW_EXTENSION_ID = os.environ['WORKFLOW_EXTENSION_ID']
REDIS_HOST_URL = os.environ['REDIS_HOST_URL']
REDIS_USERNAME = os.environ['REDIS_USERNAME']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_CHANNEL_IN = os.environ['REDIS_CHANNEL_IN']
REDIS_CHANNEL_OUT = os.environ['REDIS_CHANNEL_OUT']
REDIS_CHANNEL_READY = os.environ['REDIS_CHANNEL_READY']

def create_redis_client():
    return redis.Redis.from_url(
        REDIS_HOST_URL,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

def get_inventory_levels(shop_url: str, access_token: str, inventory_item_ids: str, location_ids: str) -> Dict[str, Any]:
    url = f"{shop_url}/admin/api/2023-04/inventory_levels.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    params = {
        "inventory_item_ids": inventory_item_ids,
        "location_ids": location_ids
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def process_message(message: str) -> Dict[str, Any]:
    data = json.loads(message)
    inputs = data['inputs']

    shop_url = inputs['shop_url']
    access_token = inputs['access_token']
    inventory_item_ids = inputs['inventory_item_ids']
    location_ids = inputs['location_ids']

    try:
        inventory_levels = get_inventory_levels(shop_url, access_token, inventory_item_ids, location_ids)
        return {
            "success": True,
            "inventory_levels": inventory_levels
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    redis_client = create_redis_client()
    pubsub = redis_client.pubsub()

    try:
        pubsub.subscribe(REDIS_CHANNEL_IN)
        redis_client.publish(REDIS_CHANNEL_READY, '')

        for message in pubsub.listen():
            if message['type'] == 'message':
                result = process_message(message['data'])

                output = {
                    "type": "completed",
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "output": result
                }
                redis_client.publish(REDIS_CHANNEL_OUT, json.dumps(output))
                break

    except Exception as e:
        error_output = {
            "type": "failed",
            "workflowInstanceId": WORKFLOW_INSTANCE_ID,
            "workflowExtensionId": WORKFLOW_EXTENSION_ID,
            "error": str(e)
        }
        redis_client.publish(REDIS_CHANNEL_OUT, json.dumps(error_output))

    finally:
        pubsub.unsubscribe(REDIS_CHANNEL_IN)
        redis_client.close()

if __name__ == "__main__":
    main()