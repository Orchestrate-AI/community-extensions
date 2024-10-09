# MailChimp-AddSubscriber Extension

This extension creates a new subscriber entry in MailChimp by adding a new email address to a specified MailChimp audience list.

## Requirements

- Python 3.9+
- Redis
- MailChimp API credentials

## Configuration

The extension requires the following inputs:

- `api_key`: Your MailChimp API key
- `server_prefix`: Your MailChimp server prefix (e.g., "us1")
- `list_id`: The ID of the MailChimp list to add the subscriber to
- `email`: The email address of the new subscriber
- `additional_fields` (optional): A dictionary of additional fields to add to the subscriber's profile

## Usage

To use this extension in your workflow, include it in your workflow configuration with the required inputs:

```yaml
name: MailChimp-AddSubscriber
description: Add a new subscriber to a MailChimp list
extensionType: container
visibility: private
configuration:
  dockerImage: your-registry/mailchimp-addsubscriber
  dockerTag: latest
inputs:
  api_key: 
    type: string
    description: MailChimp API key
  server_prefix:
    type: string
    description: MailChimp server prefix
  list_id:
    type: string
    description: MailChimp list ID
  email:
    type: string
    description: Subscriber's email address
  additional_fields:
    type: object
    description: Additional fields for the subscriber (optional)
```

## Building and Deployment

1. Build the Docker image:
   ```
   docker build -t your-registry/mailchimp-addsubscriber:latest .
   ```

2. Push the image to your Docker registry:
   ```
   docker push your-registry/mailchimp-addsubscriber:latest
   ```

3. Update your workflow configuration to use this extension, providing the necessary inputs.

## Error Handling

The extension handles errors gracefully and returns a JSON object with a `success` boolean and a `message` string. If an error occurs during the subscription process, it will be reflected in the output.

## Support

For issues or questions about this extension, please contact the extension maintainer or open an issue in the extension repository.