# MailChimp AddSubscriber Extension

This extension creates a new subscriber entry in MailChimp. It takes an email address and optional additional fields as input, and adds the subscriber to a specified MailChimp list.

## Configuration

Set the following environment variables:

- `MAILCHIMP_API_KEY`: Your MailChimp API key
- `MAILCHIMP_LIST_ID`: The ID of the MailChimp list to add subscribers to
- `MAILCHIMP_SERVER_PREFIX`: The server prefix for your MailChimp account (e.g., 'us1')

## Usage

The extension expects an input message with the following structure:

```json
{
  "email": "subscriber@example.com",
  "firstName": "John",
  "lastName": "Doe"
}
```

The `email` field is required. Any additional fields will be added as merge fields in MailChimp.

## Building and Running

1. Build the Docker image:
   ```
   docker build -t mailchimp-addsubscriber .
   ```

2. Run the container:
   ```
   docker run -p 8080:8080 -e MAILCHIMP_API_KEY=your_api_key -e MAILCHIMP_LIST_ID=your_list_id -e MAILCHIMP_SERVER_PREFIX=your_server_prefix mailchimp-addsubscriber
   ```

## Development

To run the extension locally for development:

1. Install dependencies:
   ```
   npm install
   ```

2. Set environment variables in a `.env` file

3. Run the extension:
   ```
   npm start
   ```

4. Run tests:
   ```
   npm test
   ```

## Health Check

The extension provides a health check endpoint at `/health`. You can access it at `http://localhost:8080/health` when running the container.