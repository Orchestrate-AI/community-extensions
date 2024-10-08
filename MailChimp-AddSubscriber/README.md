# MailChimp-AddSubscriber Extension

This extension creates a new subscriber entry in MailChimp. It takes the subscriber's email address and other optional details as input and adds them to a specified MailChimp list.

## Requirements

- Node.js
- Redis
- MailChimp API Key
- MailChimp Server Prefix

## Input Schema

```json
{
  "email": "string (required)",
  "firstName": "string (optional)",
  "lastName": "string (optional)",
  "listId": "string (required)"
}
```

## Output Schema

```json
{
  "success": "boolean",
  "id": "string",
  "email": "string",
  "status": "string"
}
```

## Environment Variables

- `WORKFLOW_INSTANCE_ID`: Provided by the workflow engine
- `WORKFLOW_EXTENSION_ID`: Provided by the workflow engine
- `REDIS_HOST_URL`: Redis host URL
- `REDIS_USERNAME`: Redis username
- `REDIS_PASSWORD`: Redis password
- `REDIS_CHANNEL_IN`: Redis input channel
- `REDIS_CHANNEL_OUT`: Redis output channel
- `REDIS_CHANNEL_READY`: Redis ready channel
- `MAILCHIMP_API_KEY`: Your MailChimp API key
- `MAILCHIMP_SERVER_PREFIX`: Your MailChimp server prefix

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
   docker run -e WORKFLOW_INSTANCE_ID=<value> -e WORKFLOW_EXTENSION_ID=<value> -e REDIS_HOST_URL=<value> -e REDIS_USERNAME=<value> -e REDIS_PASSWORD=<value> -e REDIS_CHANNEL_IN=<value> -e REDIS_CHANNEL_OUT=<value> -e REDIS_CHANNEL_READY=<value> -e MAILCHIMP_API_KEY=<value> -e MAILCHIMP_SERVER_PREFIX=<value> mailchimp-addsubscriber
   ```

Replace `<value>` with the appropriate values for your environment.

## Error Handling

If an error occurs during the execution, the extension will publish an error message to the `REDIS_CHANNEL_OUT` with the following structure:

```json
{
  "type": "failed",
  "workflowInstanceId": "string",
  "workflowExtensionId": "string",
  "error": "Error message"
}
```

## Support

For any issues or questions, please open an issue in the repository.