# GitHub Add Issue Comment Extension

This extension adds a comment to an existing issue on GitHub using the GitHub API.

## Requirements

- Python 3.11.10
- aiohttp
- aioredis

## Input Schema

The extension expects the following inputs:

```json
{
  "repo_owner": "string",
  "repo_name": "string",
  "issue_number": "number",
  "comment_body": "string",
  "access_token": "string"
}
```

## Output Schema

The extension returns the following output:

```json
{
  "success": "boolean",
  "comment_id": "number",
  "comment_url": "string"
}
```

In case of an error:

```json
{
  "success": false,
  "error": "string"
}
```

## Environment Variables

The extension uses the following environment variables:

- WORKFLOW_INSTANCE_ID
- WORKFLOW_EXTENSION_ID
- REDIS_HOST_URL
- REDIS_USERNAME
- REDIS_PASSWORD
- REDIS_CHANNEL_IN
- REDIS_CHANNEL_OUT
- REDIS_CHANNEL_READY

## Building and Running

1. Build the Docker image:
   ```
   docker build -t github-add-issue-comment .
   ```

2. Run the container:
   ```
   docker run -e REDIS_HOST_URL=<redis_url> -e REDIS_USERNAME=<username> -e REDIS_PASSWORD=<password> -e REDIS_CHANNEL_IN=<channel_in> -e REDIS_CHANNEL_OUT=<channel_out> -e REDIS_CHANNEL_READY=<channel_ready> -e WORKFLOW_INSTANCE_ID=<instance_id> -e WORKFLOW_EXTENSION_ID=<extension_id> github-add-issue-comment
   ```

Replace the placeholders with actual values for your environment.

## Security Note

Ensure that the GitHub access token is kept secure and not exposed in logs or error messages. It's recommended to use a GitHub App instead of a personal access token for enhanced security.

## Obtaining a GitHub Access Token

To use this extension, you need a GitHub access token with the appropriate permissions. Here's how to obtain one:

1. Go to your GitHub account settings.
2. Click on "Developer settings" in the left sidebar.
3. Click on "Personal access tokens" and then "Generate new token".
4. Give your token a descriptive name and select the "repo" scope to allow adding comments to issues.
5. Click "Generate token" and copy the token immediately (you won't be able to see it again).

Remember to keep this token secure and never share it publicly.

## Error Handling and Rate Limiting

The extension includes basic error handling and will return appropriate error messages for different types of failures. It also includes a specific check for rate limiting (403 status code) and will advise to try again later if the rate limit is exceeded.

## Logging

The extension uses Python's built-in logging module to log information about its operation. This can be helpful for debugging and monitoring the extension's behavior.

## Local Development

For local development, you can use a `.env` file to manage environment variables. Create a file named `.env` in the same directory as `main.py` and add your environment variables there:

```
REDIS_HOST_URL=your_redis_url
REDIS_USERNAME=your_redis_username
REDIS_PASSWORD=your_redis_password
REDIS_CHANNEL_IN=your_input_channel
REDIS_CHANNEL_OUT=your_output_channel
REDIS_CHANNEL_READY=your_ready_channel
WORKFLOW_INSTANCE_ID=your_instance_id
WORKFLOW_EXTENSION_ID=your_extension_id
```

Then, you can use a library like `python-dotenv` to load these variables in your local development environment.

## Testing

While this implementation doesn't include tests, it's recommended to add unit tests to ensure the functionality works as expected and to catch any regressions in future updates. You can use Python's `unittest` module or a testing framework like `pytest` to write and run tests.