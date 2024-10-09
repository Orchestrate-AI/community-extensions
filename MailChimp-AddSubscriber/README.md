# MailChimp AddSubscriber Extension

This extension creates a new subscriber entry in MailChimp. It takes an email address, first name, last name, and list ID as inputs, and adds the subscriber to the specified MailChimp list.

## Requirements

- Node.js 14 or later
- Redis server
- MailChimp API key and server prefix

## Environment Variables

The following environment variables are required:

- `WORKFLOW_INSTANCE_ID`: Unique identifier for the workflow instance
- `WORKFLOW_EXTENSION_ID`: Unique identifier for this extension
- `REDIS_HOST_URL`: URL of the Redis server
- `REDIS_USERNAME`: Redis username (optional)
- `REDIS_PASSWORD`: Redis password (optional)
- `REDIS_CHANNEL_IN`: Redis channel for incoming messages
- `REDIS_CHANNEL_OUT`: Redis channel for outgoing messages
- `REDIS_CHANNEL_READY`: Redis channel for ready signal
- `MAILCHIMP_API_KEY`: Your MailChimp API key
- `MAILCHIMP_SERVER_PREFIX`: Your MailChimp server prefix

## Input Format

The extension expects a JSON input with the following structure:

```json
{
  "email": "subscriber@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "listId": "your-mailchimp-list-id"
}
```

## Output Format

The extension will return a JSON object with the following structure:

```json
{
  "id": "subscriber-id",
  "email": "subscriber@example.com",
  "status": "subscribed"
}
```

## Error Handling

If an error occurs during the process, the extension will return an error message in the following format:

```json
{
  "type": "failed",
  "workflowInstanceId": "instance-id",
  "workflowExtensionId": "extension-id",
  "error": "Error message"
}
```

## Building and Running

1. Install dependencies:
   ```
   npm install
   ```

2. Build the Docker image:
   ```
   docker build -t mailchimp-addsubscriber .
   ```

3. Run the Docker container:
   ```
   docker run -e WORKFLOW_INSTANCE_ID=<value> -e WORKFLOW_EXTENSION_ID=<value> -e REDIS_HOST_URL=<value> -e REDIS_CHANNEL_IN=<value> -e REDIS_CHANNEL_OUT=<value> -e REDIS_CHANNEL_READY=<value> -e MAILCHIMP_API_KEY=<value> -e MAILCHIMP_SERVER_PREFIX=<value> mailchimp-addsubscriber
   ```

Replace `<value>` with the appropriate values for your environment.

## Testing

To test the extension locally:

1. Set up a `.env` file with the required environment variables.
2. Run the extension using `node index.js`.
3. Use a Redis client to publish a test message to the input channel and verify the output on the output channel.

## Support

For issues and feature requests, please open an issue in the repository.