import os
import json
import mysql.connector
from mysql.connector import Error
import redis
from dotenv import load_dotenv

load_dotenv()

# Redis connection details
REDIS_HOST_URL = os.getenv('REDIS_HOST_URL')
REDIS_USERNAME = os.getenv('REDIS_USERNAME')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_CHANNEL_IN = os.getenv('REDIS_CHANNEL_IN')
REDIS_CHANNEL_OUT = os.getenv('REDIS_CHANNEL_OUT')
REDIS_CHANNEL_READY = os.getenv('REDIS_CHANNEL_READY')

# Workflow details
WORKFLOW_INSTANCE_ID = os.getenv('WORKFLOW_INSTANCE_ID')
WORKFLOW_EXTENSION_ID = os.getenv('WORKFLOW_EXTENSION_ID')

def connect_to_mysql(host, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return connection
    except Error as e:
        raise Exception(f"Error connecting to MySQL database: {e}")

def execute_query(connection, query):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results
    except Error as e:
        raise Exception(f"Error executing MySQL query: {e}")

def process_message(message):
    try:
        data = json.loads(message)
        inputs = data['inputs']

        # Extract MySQL connection details and query from inputs
        host = inputs['host']
        user = inputs['user']
        password = inputs['password']
        database = inputs['database']
        query = inputs['query']

        # Connect to MySQL
        connection = connect_to_mysql(host, user, password, database)

        # Execute query
        results = execute_query(connection, query)

        # Close connection
        connection.close()

        return {
            'results': results,
            'row_count': len(results)
        }
    except Exception as e:
        return {
            'error': str(e)
        }

def main():
    # Connect to Redis
    redis_client = redis.Redis(
        host=REDIS_HOST_URL,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

    # Subscribe to input channel
    pubsub = redis_client.pubsub()
    pubsub.subscribe(REDIS_CHANNEL_IN)

    # Publish ready message
    redis_client.publish(REDIS_CHANNEL_READY, '')

    # Process messages
    for message in pubsub.listen():
        if message['type'] == 'message':
            result = process_message(message['data'])

            output = {
                'type': 'completed' if 'error' not in result else 'failed',
                'workflowInstanceId': WORKFLOW_INSTANCE_ID,
                'workflowExtensionId': WORKFLOW_EXTENSION_ID,
                'output': result
            }

            redis_client.publish(REDIS_CHANNEL_OUT, json.dumps(output))

            # Unsubscribe and quit after processing one message
            pubsub.unsubscribe(REDIS_CHANNEL_IN)
            break

    # Close Redis connection
    redis_client.close()

if __name__ == "__main__":
    main()