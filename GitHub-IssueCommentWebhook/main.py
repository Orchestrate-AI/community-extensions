import json
import os
import redis
import logging
import signal
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global flag for graceful shutdown
shutdown_flag = False

def process_message(message):
    """Process the incoming webhook message.

    Args:
        message (str): The JSON string containing the webhook payload.

    Returns:
        str: An empty string, as per the extension requirements.
    """
    try:
        # Parse the incoming message
        data = json.loads(message)
        logging.info(f"Received message: {data}")
        # We don't need to do anything with the data, just return an empty string
        return ""
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {e}")
        return ""

def signal_handler(signum, frame):
    """Handle termination signals for graceful shutdown.

    Args:
        signum (int): The signal number.
        frame (frame): The current stack frame.
    """
    global shutdown_flag
    logging.info(f"Received signal {signum}. Initiating graceful shutdown...")
    shutdown_flag = True

def main():
    """Main function to run the extension.

    This function sets up the Redis connection, subscribes to the input channel,
    processes incoming messages, and publishes results to the output channel.
    """
    # Redis connection details
    redis_host = os.environ['REDIS_HOST_URL']
    redis_username = os.environ['REDIS_USERNAME']
    redis_password = os.environ['REDIS_PASSWORD']
    channel_in = os.environ['REDIS_CHANNEL_IN']
    channel_out = os.environ['REDIS_CHANNEL_OUT']
    channel_ready = os.environ['REDIS_CHANNEL_READY']
    workflow_instance_id = os.environ['WORKFLOW_INSTANCE_ID']
    workflow_extension_id = os.environ['WORKFLOW_EXTENSION_ID']

    # Create Redis clients
    redis_client = redis.Redis(host=redis_host, username=redis_username, password=redis_password, decode_responses=True)
    pubsub = redis_client.pubsub()

    try:
        # Subscribe to the input channel
        pubsub.subscribe(channel_in)
        logging.info(f"Subscribed to channel: {channel_in}")

        # Publish ready message
        redis_client.publish(channel_ready, '')
        logging.info(f"Published ready message to channel: {channel_ready}")

        # Process messages
        for message in pubsub.listen():
            if shutdown_flag:
                break
            if message['type'] == 'message':
                result = process_message(message['data'])
                output = {
                    "type": "completed",
                    "workflowInstanceId": workflow_instance_id,
                    "workflowExtensionId": workflow_extension_id,
                    "output": result
                }
                redis_client.publish(channel_out, json.dumps(output))
                logging.info(f"Published result to channel: {channel_out}")
                break

    except redis.RedisError as e:
        logging.error(f"Redis error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        # Cleanup
        logging.info("Cleaning up resources...")
        pubsub.unsubscribe(channel_in)
        redis_client.close()
        logging.info("Cleanup completed. Exiting.")

if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    main()