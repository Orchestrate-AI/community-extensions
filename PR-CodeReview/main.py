import os
import sys
import logging
import redis
import json
import requests
from openai import OpenAI
from anthropic import Anthropic

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

WORKFLOW_INSTANCE_ID = os.getenv('WORKFLOW_INSTANCE_ID')
WORKFLOW_EXTENSION_ID = os.getenv('WORKFLOW_EXTENSION_ID')
REDIS_HOST_URL = os.getenv('REDIS_HOST_URL')
REDIS_USERNAME = os.getenv('REDIS_USERNAME')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_CHANNEL_IN = os.getenv('REDIS_CHANNEL_IN')
REDIS_CHANNEL_OUT = os.getenv('REDIS_CHANNEL_OUT')
REDIS_CHANNEL_READY = os.getenv('REDIS_CHANNEL_READY')

redis_client = redis.Redis.from_url(
    url=REDIS_HOST_URL,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def process_message(message):
    logger.info("Processing incoming message")
    inputs = json.loads(message)['inputs']
    pull_request_hook_body = inputs.get('pull_request_hook_body')
    openai_api_key = inputs.get('openai_api_key')
    anthropic_api_key = inputs.get('anthropic_api_key')
    model = inputs.get('model', 'gpt-4')
    github_token = inputs.get('github_token')

    if not pull_request_hook_body:
        raise ValueError("'pull_request_hook_body' is required in the input")
    if not openai_api_key and not anthropic_api_key:
        raise ValueError("Either 'openai_api_key' or 'anthropic_api_key' is required in the input")

    pr_data = json.loads(pull_request_hook_body)
    pull_request_url = pr_data['pull_request']['html_url']
    
    if pr_data['action'] != 'opened':
        logger.info("Pull request action is not 'opened'. Skipping review.")
        return {
            "pull_request_url": pull_request_url,
            "review": "",
            "model_used": None
        }

    diff_url = pr_data['pull_request']['diff_url']
    diff_content = fetch_diff(diff_url, github_token)
    review = generate_review(diff_content, model, openai_api_key, anthropic_api_key)

    return {
        "pull_request_url": pull_request_url,
        "review": review,
        "model_used": model
    }

def fetch_diff(diff_url, github_token=None):
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    response = requests.get(diff_url, headers=headers)
    response.raise_for_status()
    return response.text

def generate_review(diff_content, model, openai_api_key, anthropic_api_key):
    prompt = f"""You are an experienced software developer. Please review the following code diff and provide a concise, constructive review:

{diff_content}

Provide your review in the following format:
1. Summary (1-2 sentences)
2. Key observations (bullet points)
3. Suggestions for improvement (if any)"""

    if model.startswith('gpt-'):
        if not openai_api_key:
            raise ValueError("OpenAI API key is required for GPT models")
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful code reviewer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000
        )
        return response.choices[0].message.content
    elif model.startswith('claude-'):
        if not anthropic_api_key:
            raise ValueError("Anthropic API key is required for Claude models")
        client = Anthropic(api_key=anthropic_api_key)
        response = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ],
            system="You are a helpful code reviewer."
        )
        return response.content[0].text
    else:
        raise ValueError(f"Unsupported model: {model}")

def main():
    logger.info("Starting main function")
    redis_client.publish(REDIS_CHANNEL_READY, '')
    logger.info(f"Published ready message to channel: {REDIS_CHANNEL_READY}")

    pubsub = redis_client.pubsub()
    pubsub.subscribe(REDIS_CHANNEL_IN)
    logger.info(f"Subscribed to input channel: {REDIS_CHANNEL_IN}")

    for message in pubsub.listen():
        if message['type'] == 'message':
            logger.info("Received message from Redis")
            try:
                result = process_message(message['data'])
                output = {
                    "type": "completed",
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "output": result
                }
                redis_client.publish(REDIS_CHANNEL_OUT, json.dumps(output))
                logger.info(f"Published result to channel: {REDIS_CHANNEL_OUT}")
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}", exc_info=True)
                error_output = {
                    "type": "failed",
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "error": str(e)
                }
                redis_client.publish(REDIS_CHANNEL_OUT, json.dumps(error_output))
                logger.info(f"Published error to channel: {REDIS_CHANNEL_OUT}")
            finally:
                pubsub.unsubscribe(REDIS_CHANNEL_IN)
                logger.info(f"Unsubscribed from channel: {REDIS_CHANNEL_IN}")
                break

if __name__ == "__main__":
    logger.info("Script started")
    main()
    logger.info("Script finished")