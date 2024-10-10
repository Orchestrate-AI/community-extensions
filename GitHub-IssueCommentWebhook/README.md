# GitHub Issue Comment Webhook Extension

This extension receives a GitHub issue comment webhook and returns an empty string.

## Usage

This extension is designed to be used as part of a workflow system. It listens for incoming GitHub issue comment webhook payloads, processes them, and returns an empty string.

## Configuration

The extension requires the following environment variables to be set:

- REDIS_HOST_URL
- REDIS_USERNAME
- REDIS_PASSWORD
- REDIS_CHANNEL_IN
- REDIS_CHANNEL_OUT
- REDIS_CHANNEL_READY
- WORKFLOW_INSTANCE_ID
- WORKFLOW_EXTENSION_ID

These variables are typically set by the workflow engine when creating the extension's container.

## Building and Running

To build the Docker image:

```
docker build -t github-issue-comment-webhook .
```

To run the container:

```
docker run -e REDIS_HOST_URL=<redis_host> -e REDIS_USERNAME=<redis_username> -e REDIS_PASSWORD=<redis_password> -e REDIS_CHANNEL_IN=<channel_in> -e REDIS_CHANNEL_OUT=<channel_out> -e REDIS_CHANNEL_READY=<channel_ready> -e WORKFLOW_INSTANCE_ID=<instance_id> -e WORKFLOW_EXTENSION_ID=<extension_id> github-issue-comment-webhook
```

Replace the placeholders with actual values.

## Healthcheck

The container includes a healthcheck that verifies Redis connectivity. The Docker engine will use this to monitor the health of the container.