# Google Calendar - Create Event Extension

This extension creates an event in Google Calendar.

## Requirements

- Python 3.10
- Redis
- Google Calendar API credentials

## Usage

This extension expects the following inputs:

- `summary`: Event title (required)
- `location`: Event location (optional)
- `description`: Event description (optional)
- `start_time`: Event start time in ISO format (required)
- `end_time`: Event end time in ISO format (required)
- `time_zone`: Time zone for the event (optional, defaults to UTC)
- `google_credentials`: JSON string containing Google Calendar API credentials (required)

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
    - id: google_credentials
      name: Google Credentials
      description: JSON string containing Google Calendar API credentials
      type: string
      required: true
  outputs:
    - id: event_id
      name: Event ID
      description: The ID of the created event
      type: string
```