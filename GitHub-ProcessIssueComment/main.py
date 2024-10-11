import os
import json
import asyncio
import logging
from typing import Dict, Any
import aioredis

# Constants
REDIS_CHANNEL_IN = os.environ['REDIS_CHANNEL_IN']
REDIS_CHANNEL_OUT = os.environ['REDIS_CHANNEL_OUT']
REDIS_CHANNEL_READY = os.environ['REDIS_CHANNEL_READY']
WORKFLOW_INSTANCE_ID = os.environ['WORKFLOW_INSTANCE_ID']
WORKFLOW_EXTENSION_ID = os.environ['WORKFLOW_EXTENSION_ID']

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_message(message: str) -> Dict[str, Any]:
    """
    Process the GitHub issue comment message.

    Args:
        message (str): The input message containing comment data.

    Returns:
        Dict[str, Any]: A dictionary containing the processed comment information.
    """
    try:
        data = json.loads(message)
        inputs = data['inputs']

        # Validate required fields
        required_fields = ['comment_id', 'issue_number', 'repository', 'comment_body', 'action']
        for field in required_fields:
            if field not in inputs:
                raise ValueError(f"Missing required field: {field}")

        # Process the GitHub issue comment
        result = {
            'comment_id': inputs['comment_id'],
            'issue_number': inputs['issue_number'],
            'repository': inputs['repository'],
            'comment_body': inputs['comment_body'],
            'action': inputs['action'],
            'processed': True
        }

        logger.info(f"Processed comment {result['comment_id']} for issue {result['issue_number']}")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_message: {e}")
        raise

async def main():
    """
    Main function to handle Redis communication and message processing.
    """
    redis = await aioredis.from_url(os.environ['REDIS_HOST_URL'],
                                    username=os.environ['REDIS_USERNAME'],
                                    password=os.environ['REDIS_PASSWORD'])

    subscriber = redis.pubsub()
    await subscriber.subscribe(REDIS_CHANNEL_IN)

    logger.info("Connected to Redis and subscribed to input channel")
    await redis.publish(REDIS_CHANNEL_READY, '')
    logger.info("Published ready message")

    try:
        async for message in subscriber.listen():
            if message['type'] == 'message':
                try:
                    result = await process_message(message['data'])
                    output = {
                        'type': 'completed',
                        'workflowInstanceId': WORKFLOW_INSTANCE_ID,
                        'workflowExtensionId': WORKFLOW_EXTENSION_ID,
                        'output': result
                    }
                    await redis.publish(REDIS_CHANNEL_OUT, json.dumps(output))
                    logger.info("Published output message")
                    break
                except Exception as e:
                    error_output = {
                        'type': 'failed',
                        'workflowInstanceId': WORKFLOW_INSTANCE_ID,
                        'workflowExtensionId': WORKFLOW_EXTENSION_ID,
                        'error': str(e)
                    }
                    await redis.publish(REDIS_CHANNEL_OUT, json.dumps(error_output))
                    logger.error(f"Published error message: {str(e)}")
                    break
    finally:
        await subscriber.unsubscribe(REDIS_CHANNEL_IN)
        await redis.close()
        logger.info("Unsubscribed and closed Redis connection")

if __name__ == '__main__':
    asyncio.run(main())