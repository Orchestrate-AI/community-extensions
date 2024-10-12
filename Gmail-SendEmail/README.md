# Gmail Send Email Extension

This extension allows sending emails via Gmail using the Gmail API.

## Description

The Gmail Send Email extension is a containerized application that integrates with the workflow system to send emails through Gmail. It uses Redis for communication and the Gmail API for sending emails securely.

## Requirements

- Docker
- Access to a Gmail account with API access enabled
- Redis server

## Build and Run

1. Build the Docker image:
   ```
   docker build -t gmail-send-email .
   ```

2. Run the container:
   ```
   docker run -e WORKFLOW_INSTANCE_ID=<instance_id> \
              -e WORKFLOW_EXTENSION_ID=<extension_id> \
              -e REDIS_HOST_URL=<redis_url> \
              -e REDIS_USERNAME=<redis_username> \
              -e REDIS_PASSWORD=<redis_password> \
              -e REDIS_CHANNEL_IN=<channel_in> \
              -e REDIS_CHANNEL_OUT=<channel_out> \
              -e REDIS_CHANNEL_READY=<channel_ready> \
              gmail-send-email
   ```

## Usage

The extension expects the following inputs in the message received on REDIS_CHANNEL_IN:

- `to`: Recipient email address
- `subject`: Email subject
- `body`: Email body content
- `credentials`: JSON string containing Gmail API credentials

Example input:
```json
{
  "inputs": {
    "to": "recipient@example.com",
    "subject": "Test Email",
    "body": "This is a test email sent from the Gmail Send Email extension.",
    "credentials": "{\"token\": \"ya29.a0ARrdaM...\", \"refresh_token\": \"1//0eXfWF...\", \"token_uri\": \"https://oauth2.googleapis.com/token\", \"client_id\": \"1234567890-abcdefg...\", \"client_secret\": \"GOCSPX-ABC...\"}"
  }
}
```

## Configuration

The extension uses the following environment variables for configuration:

- WORKFLOW_INSTANCE_ID
- WORKFLOW_EXTENSION_ID
- REDIS_HOST_URL
- REDIS_USERNAME
- REDIS_PASSWORD
- REDIS_CHANNEL_IN
- REDIS_CHANNEL_OUT
- REDIS_CHANNEL_READY

These variables are set by the workflow engine when creating the extension's container.

## Extension YAML Definition

```yaml
name: Gmail Send Email
description: Sends emails via Gmail using the Gmail API
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/gmail-send-email
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: to
      name: To
      description: Recipient email address
      key: to
      type: string
      required: true
    - id: subject
      name: Subject
      description: Email subject
      key: subject
      type: string
      required: true
    - id: body
      name: Body
      description: Email body content
      key: body
      type: string
      required: true
    - id: credentials
      name: Credentials
      description: JSON string containing Gmail API credentials
      key: credentials
      type: string
      required: true
  outputs:
    - id: message_id
      name: Message ID
      description: ID of the sent email message
      key: message_id
      type: string
```

## Error Handling

If an error occurs during the email sending process, the extension will return an error message in the output:

```json
{
  "type": "failed",
  "workflowInstanceId": "<instance_id>",
  "workflowExtensionId": "<extension_id>",
  "output": {
    "error": "Error message details"
  }
}
```

## Support

For issues or questions, please open an issue in the repository or contact the extension maintainer.