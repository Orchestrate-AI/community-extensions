# Google Calendar - Create Event Extension

This extension creates an event in Google Calendar.

## Requirements

- Python 3.10
- Redis
- Google Calendar API credentials (API key or OAuth token)

## Usage

This extension expects the following inputs:

- `summary`: Event title (required)
- `location`: Event location (optional)
- `description`: Event description (optional)
- `start_time`: Event start time in ISO format (required)
- `end_time`: Event end time in ISO format (required)
- `time_zone`: Time zone for the event (optional, defaults to UTC)
- `auth_token`: Google Calendar API key or OAuth token (required)
- `is_oauth`: Set to true if using an OAuth token instead of an API key (optional, defaults to false)

## Building and Running

1. Build the Docker image:
   ```
   docker build -t google-calendar-create-event .
   ```

2. Run the container:
   ```
   docker run -e REDIS_HOST_URL=<redis_host> -e REDIS_USERNAME=<redis_username> -e REDIS_PASSWORD=<redis_password> -e REDIS_CHANNEL_IN=<channel_in> -e REDIS_CHANNEL_OUT=<channel_out> -e REDIS_CHANNEL_READY=<channel_ready> -e WORKFLOW_INSTANCE_ID=<instance_id> -e WORKFLOW_EXTENSION_ID=<extension_id> google-calendar-create-event
   ```

## Extension YAML Definition

```yaml
name: GoogleCalendar-CreateEvent
description: Create an entry into a Google calendar
extensionType: container
visibility: private
configuration:
  dockerImage: google-calendar-create-event
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: summary
      name: Event Summary
      description: The title of the event
      type: string
      required: true
    - id: location
      name: Event Location
      description: The location of the event
      type: string
      required: false
    - id: description
      name: Event Description
      description: The description of the event
      type: string
      required: false
    - id: start_time
      name: Start Time
      description: The start time of the event in ISO format
      type: string
      required: true
    - id: end_time
      name: End Time
      description: The end time of the event in ISO format
      type: string
      required: true
    - id: time_zone
      name: Time Zone
      description: The time zone for the event
      type: string
      required: false
    - id: auth_token
      name: Auth Token
      description: Google Calendar API key or OAuth token
      type: string
      required: true
    - id: is_oauth
      name: Is OAuth
      description: Set to true if using an OAuth token instead of an API key
      type: boolean
      required: false
  outputs:
    - id: event_id
      name: Event ID
      description: The ID of the created event
      type: string
```

## Authentication

This extension supports two authentication methods:

1. API Key: Use your Google Calendar API key as the `auth_token` and set `is_oauth` to false (or omit it).
2. OAuth Token: Use your OAuth token as the `auth_token` and set `is_oauth` to true.

Make sure you have the necessary permissions and have enabled the Google Calendar API in your Google Cloud Console.

## Error Handling

The extension implements error handling for common issues:

- If required inputs are missing, it will return an error.
- If there's an error when calling the Google Calendar API, it will be caught and reported.

## Performance Considerations

- This extension creates a single event per invocation.
- For bulk event creation, consider calling this extension multiple times or creating a separate bulk creation extension.

## Limitations

- The Google Calendar API has usage quotas and limits. Be mindful of how frequently you're making requests.
- This extension only creates events and does not support updating or deleting events.

## Customization

You can customize this extension further by:
- Adding support for recurring events
- Implementing event update and delete functionality
- Adding more event properties (e.g., attendees, reminders)

## Troubleshooting

If you encounter issues:

1. Ensure your Google API key or OAuth token is valid and has the necessary permissions.
2. Check if you've exceeded your API quota for the day.
3. Verify that all required inputs are provided and in the correct format.
4. Check the extension logs for any error messages or warnings.