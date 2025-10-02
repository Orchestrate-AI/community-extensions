# Redis-WorkflowProcessor Extension

This extension processes workflow steps using Redis streams. It handles incoming workflow triggers, processes messages from Redis streams, and manages callbacks from other services.

## Requirements

- Python 3.9+
- FastAPI
- aioredis
- Redis server

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`

## Configuration

Set the following environment variables:

- REDIS_HOST
- REDIS_PORT
- REDIS_PASSWORD
- WORKFLOW_INSTANCE_ID
- WORKFLOW_EXTENSION_ID
- REDIS_CHANNEL_IN
- REDIS_CHANNEL_OUT
- REDIS_CHANNEL_READY

## Usage

1. Start the server: `uvicorn main:app --reload`
2. Trigger a workflow: POST to `/trigger` with JSON body:
   ```json
   {
     "workflow_id": "example_workflow",
     "data": {
       "key": "value"
     }
   }
   ```
3. Handle callbacks: POST to `/callback` with JSON body:
   ```json
   {
     "workflow_id": "example_workflow",
     "step_id": "example_step",
     "data": {
       "key": "value"
     }
   }
   ```

## Docker

Build the Docker image:
```
docker build -t redis-workflow-processor .
```

Run the container:
```
docker run -p 8000:8000 -e REDIS_HOST=host.docker.internal redis-workflow-processor
```

## Extension YAML Definition

```yaml
name: Redis-WorkflowProcessor
description: Processes workflow steps using Redis streams
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/redis-workflow-processor
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: workflow_id
      name: Workflow ID
      description: Unique identifier for the workflow
      key: workflow_id
      type: string
      required: true
    - id: data
      name: Workflow Data
      description: Data associated with the workflow
      key: data
      type: object
      required: true
  outputs:
    - id: result
      name: Processing Result
      description: Result of the workflow processing
      key: result
      type: object
```