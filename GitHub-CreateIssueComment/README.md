# GitHub Issue Comment Extension

This extension creates a comment on a specified GitHub issue using the GitHub API.

## Description

This extension uses the GitHub API to post a comment on a given issue in a specified repository. It's designed to work within a workflow system that uses Redis for communication.

## Requirements

- Node.js 18 LTS
- Redis
- GitHub Personal Access Token with repo scope

## Configuration

The following environment variables are required:

- WORKFLOW_INSTANCE_ID
- WORKFLOW_EXTENSION_ID
- REDIS_HOST_URL
- REDIS_USERNAME
- REDIS_PASSWORD
- REDIS_CHANNEL_IN
- REDIS_CHANNEL_OUT
- REDIS_CHANNEL_READY

## Input Schema

The extension expects the following inputs:

```json
{
  "github_token": "your_github_personal_access_token",
  "owner": "repository_owner",
  "repo": "repository_name",
  "issue_number": 123,
  "comment": "Your comment text here"
}
```

## Output Schema

The extension will return the following output:

```json
{
  "success": true,
  "comment_id": 1234567890,
  "comment_url": "https://github.com/owner/repo/issues/123#issuecomment-1234567890"
}
```

In case of an error:

```json
{
  "success": false,
  "error": "Error message"
}
```

## Usage

1. Ensure all required environment variables are set.
2. Run the extension using `node index.js`.
3. The extension will connect to Redis, wait for input on the specified channel, process the request, and return the result.

## Error Handling

The extension includes error handling for input validation, GitHub API requests, and Redis communication. Errors are logged to the console and returned in the output.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Extension Configuration

```yaml
name: GitHub-CreateIssueComment
description: Creates a comment on a specified GitHub issue
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/github-create-issue-comment
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: github_token
      name: GitHub Token
      description: GitHub Personal Access Token with repo scope
      key: github_token
      type: string
      required: true
    - id: owner
      name: Repository Owner
      description: Owner of the GitHub repository
      key: owner
      type: string
      required: true
    - id: repo
      name: Repository Name
      description: Name of the GitHub repository
      key: repo
      type: string
      required: true
    - id: issue_number
      name: Issue Number
      description: Number of the issue to comment on
      key: issue_number
      type: integer
      required: true
    - id: comment
      name: Comment Text
      description: Text content of the comment to be posted
      key: comment
      type: string
      required: true
  outputs:
    - id: success
      name: Success
      description: Indicates whether the comment was successfully created
      key: success
      type: boolean
    - id: comment_id
      name: Comment ID
      description: ID of the created comment
      key: comment_id
      type: integer
    - id: comment_url
      name: Comment URL
      description: URL of the created comment
      key: comment_url
      type: string
    - id: error
      name: Error Message
      description: Error message if the operation failed
      key: error
      type: string
```