# GitHub Webhook Handler Extension

This extension processes GitHub webhook payloads and returns an empty string when the 'action' field is 'created'.

## Description

The GitHub Webhook Handler is a simple extension that listens for webhook payloads from GitHub. It specifically checks for the 'action' field in the payload. If the action is 'created', it returns an empty string. For all other actions, it returns null.

## Requirements

- Python 3.10
- aioredis 2.0.1

## Usage

This extension is designed to be used within a workflow system that uses Redis for communication. It expects certain environment variables to be set:

- WORKFLOW_INSTANCE_ID
- WORKFLOW_EXTENSION_ID
- REDIS_HOST_URL
- REDIS_USERNAME
- REDIS_PASSWORD
- REDIS_CHANNEL_IN
- REDIS_CHANNEL_OUT
- REDIS_CHANNEL_READY

The extension will listen for messages on the REDIS_CHANNEL_IN, process them, and publish results to REDIS_CHANNEL_OUT.

## Building and Running

To build the Docker image:

```
docker build -t github-webhook-handler .
```

To run the extension (environment variables should be provided by the workflow system):

```
docker run --env-file .env github-webhook-handler
```

## Extension YAML Definition

```yaml
name: GitHub Webhook Handler
description: Processes GitHub webhook payloads and returns an empty string when the 'action' field is 'created'
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/github-webhook-handler
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: webhook-payload
      name: Webhook Payload
      description: The GitHub webhook payload
      key: payload
      type: object
      required: true
  outputs:
    - id: result
      name: Result
      description: Empty string if action is 'created', null otherwise
      key: result
      type: string
```

## Error Handling

The extension includes basic error handling for JSON parsing errors and general exceptions. All errors are logged to stdout.

## Security Considerations

This extension does not implement any additional security measures beyond what's provided by the workflow system. Ensure that your workflow system properly validates and secures incoming webhook payloads before passing them to this extension.