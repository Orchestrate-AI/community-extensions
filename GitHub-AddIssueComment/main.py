import os
import json
import asyncio
import aiohttp
import logging
from aioredis import Redis
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def add_comment_to_issue(repo_owner: str, repo_name: str, issue_number: int, comment_body: str, access_token: str) -> Dict[str, Any]:
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment_body}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 201:
                return await response.json()
            elif response.status == 403:
                raise Exception("Rate limit exceeded. Please try again later.")
            else:
                raise Exception(f"Failed to add comment: {response.status} {await response.text()}")

def validate_inputs(inputs: Dict[str, Any]) -> None:
    required_fields = ['repo_owner', 'repo_name', 'issue_number', 'comment_body', 'access_token']
    for field in required_fields:
        if field not in inputs:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(inputs['issue_number'], int):
        raise ValueError("issue_number must be an integer")

async def process_message(message: str) -> Dict[str, Any]:
    try:
        data = json.loads(message)
        inputs = data['inputs']

        validate_inputs(inputs)

        repo_owner = inputs['repo_owner']
        repo_name = inputs['repo_name']
        issue_number = inputs['issue_number']
        comment_body = inputs['comment_body']
        access_token = inputs['access_token']

        result = await add_comment_to_issue(repo_owner, repo_name, issue_number, comment_body, access_token)
        logger.info(f"Successfully added comment to issue {issue_number} in {repo_owner}/{repo_name}")
        return {
            "success": True,
            "comment_id": result['id'],
            "comment_url": result['html_url']
        }
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def main() -> None:
    redis = Redis.from_url(
        os.environ['REDIS_HOST_URL'],
        username=os.environ['REDIS_USERNAME'],
        password=os.environ['REDIS_PASSWORD']
    )

    channel_in = os.environ['REDIS_CHANNEL_IN']
    channel_out = os.environ['REDIS_CHANNEL_OUT']
    channel_ready = os.environ['REDIS_CHANNEL_READY']

    await redis.publish(channel_ready, '')
    logger.info("Extension ready to process messages")

    while True:
        try:
            message = await redis.blpop(channel_in, timeout=0)
            if message:
                logger.info("Received message, processing...")
                result = await process_message(message[1])
                await redis.publish(channel_out, json.dumps({
                    "type": "completed",
                    "workflowInstanceId": os.environ['WORKFLOW_INSTANCE_ID'],
                    "workflowExtensionId": os.environ['WORKFLOW_EXTENSION_ID'],
                    "output": result
                }))
                logger.info("Message processed and result published")
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())