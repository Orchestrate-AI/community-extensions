# GitHub-AddIssueComment Extension

This extension adds a comment to an existing GitHub issue using a GitHub App with private key authentication.

## Description

The GitHub-AddIssueComment extension is designed to work within a workflow system that uses Redis for communication. It receives input data through a Redis channel, processes the request to add a comment to a GitHub issue, and returns the result through another Redis channel.

## Requirements

- Python 3.9+
- Redis
- GitHub App with appropriate permissions

## Configuration

The extension requires the following environment variables:

- WORKFLOW_INSTANCE_ID
- WORKFLOW_EXTENSION_ID
- REDIS_HOST_URL
- REDIS_USERNAME
- REDIS_PASSWORD
- REDIS_CHANNEL_IN
- REDIS_CHANNEL_OUT
- REDIS_CHANNEL_READY
- GITHUB_APP_ID
- GITHUB_PRIVATE_KEY
- GITHUB_INSTALLATION_ID

These are provided by the workflow engine when the extension is executed.

## Input

The extension expects the following inputs in the message received on REDIS_CHANNEL_IN:

```json
{
  "inputs": {
    "repo_name": "owner/repo",
    "issue_number": "123",
    "comment": "This is the comment to be added to the issue"
  }
}
```

## Output

The extension will publish the result to REDIS_CHANNEL_OUT in the following format:

```json
{
  "type": "completed",
  "workflowInstanceId": "instance_id",
  "workflowExtensionId": "extension_id",
  "output": {
    "status": "success",
    "comment_id": 123456,
    "comment_url": "https://github.com/owner/repo/issues/123#issuecomment-123456"
  }
}
```

In case of an error:

```json
{
  "type": "failed",
  "workflowInstanceId": "instance_id",
  "workflowExtensionId": "extension_id",
  "output": {
    "status": "error",
    "error_message": "Error message details"
  }
}
```

## Building and Running

To build the Docker image:

```
docker build -t github-addissuecomment .
```

The extension is designed to be run as part of a larger workflow system. The workflow engine is responsible for creating the container with the appropriate environment variables and Redis connection details.

## Security Considerations

- The GitHub App's private key is sensitive information. Ensure it's securely passed to the extension and not logged or exposed.
- The extension uses JWT for authentication with GitHub, which is a secure method for GitHub App authentication.

## Error Handling

The extension includes error handling for various scenarios, including missing parameters and GitHub API errors. All exceptions are caught and returned as error messages in the output. Errors are also logged for debugging purposes.

## Logging

The extension uses Python's built-in logging module to log information and errors. This helps with monitoring and debugging the extension's operation.

## Extension YAML Definition

```yaml
name: GitHub-AddIssueComment
description: Adds a comment to an existing GitHub issue using a GitHub App with private key authentication
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/github-addissuecomment
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: repo-name
      name: Repository Name
      description: The full name of the repository (owner/repo)
      key: repo_name
      type: string
      required: true
    - id: issue-number
      name: Issue Number
      description: The number of the issue to comment on
      key: issue_number
      type: string
      required: true
    - id: comment
      name: Comment
      description: The comment to be added to the issue
      key: comment
      type: string
      required: true
  outputs:
    - id: comment-id
      name: Comment ID
      description: The ID of the created comment
      key: comment_id
      type: number
    - id: comment-url
      name: Comment URL
      description: The URL of the created comment
      key: comment_url
      type: string
```

This YAML configuration defines the extension's properties, inputs, and outputs for use in the workflow system.