import os
import json
import mysql.connector
from mysql.connector import Error
import redis

# Redis connection details
REDIS_HOST_URL = os.environ['REDIS_HOST_URL']
REDIS_USERNAME = os.environ['REDIS_USERNAME']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_CHANNEL_IN = os.environ['REDIS_CHANNEL_IN']
REDIS_CHANNEL_OUT = os.environ['REDIS_CHANNEL_OUT']
REDIS_CHANNEL_READY = os.environ['REDIS_CHANNEL_READY']
WORKFLOW_INSTANCE_ID = os.environ['WORKFLOW_INSTANCE_ID']
WORKFLOW_EXTENSION_ID = os.environ['WORKFLOW_EXTENSION_ID']

def execute_query(host, user, password, database, query):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            return results
    except Error as e:
        return {"error": str(e)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def process_message(message):
    try:
        data = json.loads(message)
        inputs = data['inputs']
        
        host = inputs.get('host')
        user = inputs.get('user')
        password = inputs.get('password')
        database = inputs.get('database')
        query = inputs.get('query')
        
        if not all([host, user, password, database, query]):
            return {"error": "Missing required input parameters"}
        
        results = execute_query(host, user, password, database, query)
        return {"results": results}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in input message"}
    except Exception as e:
        return {"error": str(e)}

def main():
    redis_client = redis.Redis(
        host=REDIS_HOST_URL,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        decode_responses=True
    )
    pubsub = redis_client.pubsub()
    
    # Subscribe to input channel
    pubsub.subscribe(REDIS_CHANNEL_IN)
    
    # Publish ready message
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
            break  # Exit after processing one message
    
    pubsub.unsubscribe(REDIS_CHANNEL_IN)
    redis_client.close()

if __name__ == "__main__":
    main()