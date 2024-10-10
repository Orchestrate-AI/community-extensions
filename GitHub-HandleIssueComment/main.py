import os
import json
import logging
from typing import Dict, Any

import redis
from github import Github, GithubException

# Environment variables
WORKFLOW_INSTANCE_ID = os.environ['WORKFLOW_INSTANCE_ID']
WORKFLOW_EXTENSION_ID = os.environ['WORKFLOW_EXTENSION_ID']
REDIS_HOST_URL = os.environ['REDIS_HOST_URL']
REDIS_USERNAME = os.environ['REDIS_USERNAME']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_CHANNEL_IN = os.environ['REDIS_CHANNEL_IN']
REDIS_CHANNEL_OUT = os.environ['REDIS_CHANNEL_OUT']
REDIS_CHANNEL_READY = os.environ['REDIS_CHANNEL_READY']

# Constants
ACTION_ADD_COMMENT = 'add_comment'
ACTION_EDIT_COMMENT = 'edit_comment'
ACTION_DELETE_COMMENT = 'delete_comment'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Redis clients
redis_client = redis.Redis.from_url(
    REDIS_HOST_URL,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD
)
pubsub = redis_client.pubsub()

def process_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the incoming message and perform the requested GitHub action.

    :param message: The message received from Redis
    :return: A dictionary containing the result of the action
    """
    try:
        data = json.loads(message['data'])
        inputs = data['inputs']
        
        # Validate inputs
        required_fields = ['github_token', 'repo_name', 'issue_number', 'action']
        for field in required_fields:
            if field not in inputs:
                raise ValueError(f"Missing required input: {field}")
        
        # Initialize GitHub client
        github_token = inputs['github_token']
        g = Github(github_token)
        
        # Get repository and issue
        repo = g.get_repo(inputs['repo_name'])
        issue = repo.get_issue(number=inputs['issue_number'])
        
        # Perform action based on input
        action = inputs['action']
        if action == ACTION_ADD_COMMENT:
            comment = issue.create_comment(inputs['comment_text'])
            result = {'comment_id': comment.id, 'comment_url': comment.html_url}
        elif action == ACTION_EDIT_COMMENT:
            comment = issue.get_comment(inputs['comment_id'])
            comment.edit(inputs['new_comment_text'])
            result = {'comment_id': comment.id, 'comment_url': comment.html_url}
        elif action == ACTION_DELETE_COMMENT:
            comment = issue.get_comment(inputs['comment_id'])
            comment.delete()
            result = {'status': 'deleted'}
        else:
            raise ValueError(f'Invalid action: {action}')
        
        logger.info(f"Action {action} completed successfully")
        return result
    except GithubException as ge:
        logger.error(f"GitHub API error: {ge}")
        return {'error': f"GitHub API error: {ge.data.get('message', str(ge))}"}
    except ValueError as ve:
        logger.error(f"Value error: {ve}")
        return {'error': str(ve)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {'error': f"Unexpected error: {str(e)}"}

def main():
    """
    Main function to handle the extension's lifecycle.
    """
    try:
        # Subscribe to input channel
        pubsub.subscribe(REDIS_CHANNEL_IN)
        logger.info(f"Subscribed to channel: {REDIS_CHANNEL_IN}")
        
        # Publish ready message
        redis_client.publish(REDIS_CHANNEL_READY, '')
        logger.info(f"Published ready message to channel: {REDIS_CHANNEL_READY}")
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                logger.info("Received message, processing...")
                result = process_message(message)
                
                output = {
                    'type': 'completed',
                    'workflowInstanceId': WORKFLOW_INSTANCE_ID,
                    'workflowExtensionId': WORKFLOW_EXTENSION_ID,
                    'output': result
                }
                
                redis_client.publish(REDIS_CHANNEL_OUT, json.dumps(output))
                logger.info(f"Published result to channel: {REDIS_CHANNEL_OUT}")
                
                # Unsubscribe and quit after processing one message
                pubsub.unsubscribe(REDIS_CHANNEL_IN)
                logger.info(f"Unsubscribed from channel: {REDIS_CHANNEL_IN}")
                break
    except Exception as e:
        logger.error(f"Error in main function: {e}")
    finally:
        # Cleanup
        pubsub.close()
        redis_client.close()
        logger.info("Cleaned up Redis connections")

if __name__ == '__main__':
    main()