# GitHub-ProcessIssueComment Extension

This extension processes GitHub issue comments within a workflow system. It receives information about a comment on a GitHub issue, processes it, and returns a structured output.

## Description

The GitHub-ProcessIssueComment extension is designed to handle events related to comments on GitHub issues. It can process various actions such as comment creation, editing, or deletion. The extension receives the comment data, performs any necessary processing, and returns the results in a structured format.

## Requirements

- Docker
- Access to a Redis instance

## Building and Running

1. Build the Docker image:
   ```
   docker build -t github-process-issue-comment .
   ```

2. Run the extension (environment variables will be provided by the workflow engine):
   ```
   docker run --env-file .env github-process-issue-comment
   ```

## Configuration

The extension uses the following environment variables:

- WORKFLOW_INSTANCE_ID
- WORKFLOW_EXTENSION_ID
- REDIS_HOST_URL
- REDIS_USERNAME
- REDIS_PASSWORD
- REDIS_CHANNEL_IN
- REDIS_CHANNEL_OUT
- REDIS_CHANNEL_READY

These are provided by the workflow engine and should not be modified.

## Input

The extension expects an input message with the following structure:

```json
{
  "inputs": {
    "comment_id": "12345",
    "issue_number": "67",
    "repository": "owner/repo",
    "comment_body": "This is a comment",
    "action": "created"
  }
}
```

## Output

The extension produces an output message with the following structure:

```json
{
  "comment_id": "12345",
  "issue_number": "67",
  "repository": "owner/repo",
  "comment_body": "This is a comment",
  "action": "created",
  "processed": true
}
```

## Error Handling

If an error occurs during processing, the extension will publish an error message to the output channel with details about the error.

## Extension YAML Definition

```yaml
name: GitHub-ProcessIssueComment
description: Processes GitHub issue comments within a workflow system
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/github-process-issue-comment
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: comment_id
      name: Comment ID
      description: The ID of the GitHub comment
      key: comment_id
      type: string
      required: true
    - id: issue_number
      name: Issue Number
      description: The number of the GitHub issue
      key: issue_number
      type: string
      required: true
    - id: repository
      name: Repository
      description: The GitHub repository in the format owner/repo
      key: repository
      type: string
      required: true
    - id: comment_body
      name: Comment Body
      description: The content of the comment
      key: comment_body
      type: string
      required: true
    - id: action
      name: Action
      description: The action performed on the comment (e.g., created, edited, deleted)
      key: action
      type: string
      required: true
  outputs:
    - id: processed_comment
      name: Processed Comment
      description: The processed comment information
      key: processed_comment
      type: object
```

## Support

For issues and questions, please open an issue in the extension's GitHub repository.