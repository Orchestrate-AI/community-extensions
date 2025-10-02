import os
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from aioredis import Redis
from aioredis.exceptions import RedisError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
WORKFLOW_INSTANCE_ID = os.getenv("WORKFLOW_INSTANCE_ID")
WORKFLOW_EXTENSION_ID = os.getenv("WORKFLOW_EXTENSION_ID")
REDIS_CHANNEL_IN = os.getenv("REDIS_CHANNEL_IN")
REDIS_CHANNEL_OUT = os.getenv("REDIS_CHANNEL_OUT")
REDIS_CHANNEL_READY = os.getenv("REDIS_CHANNEL_READY")

# Initialize Redis connection
redis = Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)

class WorkflowTrigger(BaseModel):
    workflow_id: str
    data: Dict[str, Any]

class CallbackData(BaseModel):
    workflow_id: str
    step_id: str
    data: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    try:
        await redis.ping()
        logger.info("Connected to Redis successfully")
        await redis.publish(REDIS_CHANNEL_READY, "")
        logger.info(f"Published ready message to {REDIS_CHANNEL_READY}")
    except RedisError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    await redis.close()
    logger.info("Closed Redis connection")

async def process_message(message: Dict[str, Any]):
    try:
        # Process the message here
        logger.info(f"Processing message: {message}")
        result = {"result": f"Processed: {message['data']}"}
        
        # Publish the result to the output channel
        await redis.publish(REDIS_CHANNEL_OUT, json.dumps({
            "type": "completed",
            "workflowInstanceId": WORKFLOW_INSTANCE_ID,
            "workflowExtensionId": WORKFLOW_EXTENSION_ID,
            "output": result
        }))
        logger.info(f"Published result to {REDIS_CHANNEL_OUT}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await redis.publish(REDIS_CHANNEL_OUT, json.dumps({
            "type": "failed",
            "workflowInstanceId": WORKFLOW_INSTANCE_ID,
            "workflowExtensionId": WORKFLOW_EXTENSION_ID,
            "error": str(e)
        }))

@app.post("/trigger")
async def trigger_workflow(workflow: WorkflowTrigger, background_tasks: BackgroundTasks):
    try:
        message = {
            "workflow_id": workflow.workflow_id,
            "data": workflow.data
        }
        await redis.publish(REDIS_CHANNEL_IN, json.dumps(message))
        background_tasks.add_task(process_message, message)
        return JSONResponse(content={"status": "Workflow triggered"}, status_code=202)
    except RedisError as e:
        logger.error(f"Redis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger workflow")

@app.post("/callback")
async def handle_callback(callback: CallbackData):
    try:
        await redis.publish(REDIS_CHANNEL_IN, json.dumps(callback.dict()))
        return {"status": "Callback received"}
    except RedisError as e:
        logger.error(f"Redis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process callback")

async def consume_messages():
    try:
        while True:
            message = await redis.xread({REDIS_CHANNEL_IN: "0"}, count=1, block=0)
            if message:
                for _, messages in message:
                    for msg_id, msg_data in messages:
                        await process_message(json.loads(msg_data['message']))
                        await redis.xdel(REDIS_CHANNEL_IN, msg_id)
    except RedisError as e:
        logger.error(f"Error consuming messages: {e}")

@app.on_event("startup")
async def start_consumer():
    background_tasks = BackgroundTasks()
    background_tasks.add_task(consume_messages)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)