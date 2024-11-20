# GitHub-HandleIssueComment Extension

This extension interacts with GitHub to handle issue comments. It can add, edit, or delete comments on GitHub issues using the provided GitHub API token.

## Requirements

- Docker
- Access to a Redis instance
- GitHub API token with appropriate permissions

## Usage

The extension expects the following inputs in the message:

- `github_token`: Your GitHub API token
- `repo_name`: The repository name in the format "owner/repo"
- `issue_number`: The issue number to interact with
- `action`: One of "add_comment", "edit_comment", or "delete_comment"
- `comment_text`: The text of the comment (for add_comment action)
- `comment_id`: The ID of the comment to edit or delete (for edit_comment and delete_comment actions)
- `new_comment_text`: The new text for the comment (for edit_comment action)

## Building and Running

1. Build the Docker image:
   ```
   docker build -t github-handle-issue-comment .
   ```

2. Run the container, providing the necessary environment variables:
   ```
   docker run -e WORKFLOW_INSTANCE_ID=<instance_id> \
              -e WORKFLOW_EXTENSION_ID=<extension_id> \
              -e REDIS_HOST_URL=<redis_url> \
              -e REDIS_USERNAME=<redis_username> \
              -e REDIS_PASSWORD=<redis_password> \
              -e REDIS_CHANNEL_IN=<input_channel> \
              -e REDIS_CHANNEL_OUT=<output_channel> \
              -e REDIS_CHANNEL_READY=<ready_channel> \
              github-handle-issue-comment
   ```

## Extension YAML Definition

```yaml
name: GitHub-HandleIssueComment
description: Handles GitHub issue comments (add, edit, delete)
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/github-handle-issue-comment
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: github_token
      name: GitHub API Token
      description: GitHub API token with appropriate permissions
      key: github_token
      type: string
      required: true
    - id: repo_name
      name: Repository Name
      description: The repository name in the format "owner/repo"
      key: repo_name
      type: string
      required: true
    - id: issue_number
      name: Issue Number
      description: The issue number to interact with
      key: issue_number
      type: number
      required: true
    - id: action
      name: Action
      description: The action to perform (add_comment, edit_comment, delete_comment)
      key: action
      type: string
      required: true
    - id: comment_text
      name: Comment Text
      description: The text of the comment (for add_comment action)
      key: comment_text
      type: string
      required: false
    - id: comment_id
      name: Comment ID
      description: The ID of the comment to edit or delete (for edit_comment and delete_comment actions)
      key: comment_id
      type: number
      required: false
    - id: new_comment_text
      name: New Comment Text
      description: The new text for the comment (for edit_comment action)
      key: new_comment_text
      type: string
      required: false
  outputs:
    - id: result
      name: Result
      description: The result of the GitHub action
      key: result
      type: object
```

## Error Handling

The extension includes error handling for various scenarios, including GitHub API errors and input validation. Error messages will be returned in the output with an 'error' key.

## Logging

The extension uses Python's logging module to log important events and errors, which can be useful for debugging and monitoring.
