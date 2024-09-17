import os
import json
import asyncio
from redis.asyncio import Redis
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

load_dotenv()

WORKFLOW_INSTANCE_ID = os.getenv('WORKFLOW_INSTANCE_ID')
WORKFLOW_EXTENSION_ID = os.getenv('WORKFLOW_EXTENSION_ID')
REDIS_HOST_URL = os.getenv('REDIS_HOST_URL')
REDIS_USERNAME = os.getenv('REDIS_USERNAME')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_CHANNEL_IN = os.getenv('REDIS_CHANNEL_IN')
REDIS_CHANNEL_OUT = os.getenv('REDIS_CHANNEL_OUT')
REDIS_CHANNEL_READY = os.getenv('REDIS_CHANNEL_READY')

async def fetch_youtube_comments(video_id, auth_token, max_comments, is_oauth=False):
    if is_oauth:
        credentials = Credentials(auth_token)
        youtube = build('youtube', 'v3', credentials=credentials)
    else:
        youtube = build('youtube', 'v3', developerKey=auth_token)
    
    try:
        comments = []
        next_page_token = None

        while len(comments) < max_comments:
            response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(max_comments - len(comments), 100),
                pageToken=next_page_token,
                textFormat='plainText'
            ).execute()

            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'author': comment['authorDisplayName'],
                    'text': comment['textDisplay'],
                    'published_at': comment['publishedAt'],
                    'like_count': comment['likeCount']
                })

            next_page_token = response.get('nextPageToken')
            if not next_page_token or len(comments) >= max_comments:
                break

        return comments[:max_comments]
    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred: {e.content}')
        raise

async def process_message(message):
    data = json.loads(message)
    inputs = data.get('inputs', {})
    
    video_id = inputs.get('video_id')
    auth_token = inputs.get('auth_token')
    max_comments = inputs.get('max_comments', 100)
    is_oauth = inputs.get('is_oauth', False)
    
    if not video_id or not auth_token:
        raise ValueError("'video_id' and 'auth_token' are required in the input")
    
    try:
        max_comments = int(max_comments)
    except ValueError:
        raise ValueError("'max_comments' must be a valid integer")
    
    if max_comments < 1:
        raise ValueError("'max_comments' must be at least 1")
    
    # Handle different formats for is_oauth
    if isinstance(is_oauth, str):
        is_oauth = is_oauth.lower() == 'true'
    
    comments = await fetch_youtube_comments(video_id, auth_token, max_comments, is_oauth)
    
    return {
        "comments": comments,
        "video_id": video_id,
        "total_results": len(comments)
    }

async def main():
    redis = Redis.from_url(
        REDIS_HOST_URL,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD
    )

    await redis.publish(REDIS_CHANNEL_READY, '')

    pubsub = redis.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL_IN)

    async for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                result = await process_message(message['data'])
                output = {
                    "type": "completed",
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "output": result
                }
            except Exception as e:
                output = {
                    "type": "failed",
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "error": str(e)
                }
            
            await redis.publish(REDIS_CHANNEL_OUT, json.dumps(output))
            await redis.close()
            break

    await pubsub.unsubscribe(REDIS_CHANNEL_IN)
    await redis.close()

if __name__ == "__main__":
    asyncio.run(main())