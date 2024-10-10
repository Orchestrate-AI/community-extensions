import os
import json
import redis
import requests
from github import Github
from github import GithubIntegration
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Redis configuration
REDIS_HOST_URL = os.environ['REDIS_HOST_URL']
REDIS_USERNAME = os.environ['REDIS_USERNAME']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_CHANNEL_IN = os.environ['REDIS_CHANNEL_IN']
REDIS_CHANNEL_OUT = os.environ['REDIS_CHANNEL_OUT']
REDIS_CHANNEL_READY = os.environ['REDIS_CHANNEL_READY']

def add_issue_comment(repo_name, issue_number, comment_body, github_app_id, github_private_key, github_installation_id):
    integration = GithubIntegration(github_app_id, github_private_key)
    github_connection = integration.get_github_for_installation(github_installation_id)
    
    try:
        repo = github_connection.get_repo(repo_name)
        issue = repo.get_issue(number=issue_number)
        comment = issue.create_comment(comment_body)
        
        return {
            "status": "success",
            "comment_id": comment.id,
            "comment_url": comment.html_url
        }
    except Exception as e:
        logging.error(f"Error adding comment: {str(e)}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def process_message(message):
    try:
        data = json.loads(message)
        inputs = data['inputs']
        
        repo_name = inputs.get('repo_name')
        issue_number = inputs.get('issue_number')
        comment_body = inputs.get('comment')
        github_app_id = inputs.get('github_app_id')
        github_private_key = inputs.get('github_private_key')
        github_installation_id = inputs.get('github_installation_id')

        if not all([repo_name, issue_number, comment_body, github_app_id, github_private_key, github_installation_id]):
            raise ValueError("Missing required parameters")

        issue_number = int(issue_number)  # Ensure issue_number is an integer
        
        return add_issue_comment(repo_name, issue_number, comment_body, github_app_id, github_private_key, github_installation_id)
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def main():
    publisher = redis.Redis.from_url(REDIS_HOST_URL, username=REDIS_USERNAME, password=REDIS_PASSWORD)
    subscriber = redis.Redis.from_url(REDIS_HOST_URL, username=REDIS_USERNAME, password=REDIS_PASSWORD)

    pubsub = subscriber.pubsub()
    pubsub.subscribe(REDIS_CHANNEL_IN)

    publisher.publish(REDIS_CHANNEL_READY, '')

    logging.info("Listening for messages...")

    for message in pubsub.listen():
        if message['type'] == 'message':
            result = process_message(message['data'])

            output = {
                'type': 'completed' if result['status'] == 'success' else 'failed',
                'workflowInstanceId': os.environ['WORKFLOW_INSTANCE_ID'],
                'workflowExtensionId': os.environ['WORKFLOW_EXTENSION_ID'],
                'output': result
            }
            publisher.publish(REDIS_CHANNEL_OUT, json.dumps(output))

            if result['status'] == 'error':
                logging.error(f"Error occurred: {result['error_message']}")

            pubsub.unsubscribe(REDIS_CHANNEL_IN)
            break

    publisher.close()
    subscriber.close()

if __name__ == "__main__":
    main()