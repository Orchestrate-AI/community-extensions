# YouTube Comments Fetcher Extension

This extension retrieves comments from a specified YouTube video using the Google API. The number of comments to fetch is configurable, allowing for flexible usage within your workflows.

## Inputs

1. `video_id` (required):
   - Type: string
   - Description: The ID of the YouTube video to fetch comments from
   - Example: "dQw4w9WgXcQ"

2. `auth_token` (required):
   - Type: string
   - Description: Your Google API key or OAuth token for authentication

3. `is_oauth` (optional):
   - Type: boolean or string
   - Description: Set to true if using an OAuth token instead of an API key
   - Default: false
   - Note: Accepts boolean true/false or string "true"/"True" (case-insensitive)

4. `max_comments` (optional):
   - Type: number
   - Description: The maximum number of comments to fetch
   - Default: 100
   - Note: You can specify any number of comments to fetch. The extension will paginate through the results to fetch the requested number of comments.

## Outputs

1. `comments`:
   - Type: array of objects
   - Description: An array containing the fetched comments from the specified video
   - Each comment object includes:
     - `author`: The name of the comment author
     - `text`: The content of the comment
     - `published_at`: The timestamp when the comment was published
     - `like_count`: The number of likes on the comment

2. `video_id`:
   - Type: string
   - Description: The ID of the video that was processed (echoed from input)

3. `total_results`:
   - Type: number
   - Description: The total number of comments fetched

## Resource Requirements

This extension has minimal resource requirements:

- CPU: 0.1 vCPU (1/10th of a CPU core) should be sufficient for most use cases
- Memory: 128MB RAM should be adequate

For high-volume scenarios or if you need to process multiple videos in parallel, consider increasing these resources:

- CPU: 0.25 vCPU
- Memory: 256MB RAM

## Implementation Details

The extension uses the YouTube Data API v3 to fetch comments. It makes multiple API calls if necessary to retrieve the requested number of comments. Here are some key points about the implementation:

- The extension fetches comments in batches of up to 100 at a time, which is the maximum allowed by the YouTube API for a single request.
- If more than 100 comments are requested, the extension will make multiple API calls and paginate through the results to fetch the desired number of comments.
- The total number of comments fetched will be the number specified in the `max_comments` input parameter.
- The `is_oauth` parameter supports boolean values (true/false) as well as string values ("true"/"True", case-insensitive).

The extension is implemented in Python and uses the following main libraries:
- `google-api-python-client` for interacting with the YouTube API
- `redis` for communication within the OrchestrateAI workflow system

### API Scope

This extension requires the following YouTube API scope:

```
https://www.googleapis.com/auth/youtube.force-ssl
```

This scope is necessary for accessing the `commentThreads` endpoint, even for read-only operations. If you're using OAuth authentication, ensure that your OAuth 2.0 credentials in the Google Developer Console have this scope enabled, and that your application requests this scope during the OAuth flow when obtaining the access token.

If you're using an API key (when `is_oauth` is false), you don't need to specify a scope. API keys have their own set of quotas and limitations defined in the Google Developer Console.

## Error Handling

The extension implements error handling for common issues:

- If the video ID or auth token is missing, it will return an error.
- If there's an HTTP error when calling the YouTube API, it will be caught and reported.
- If the provided `max_comments` value is less than 1, it will raise an error.

## Performance Considerations

- The extension fetches comments in batches of up to 100 to optimize API usage and performance.
- It's designed to be efficient for videos with a large number of comments, as it uses pagination to fetch the required number of comments.
- Multiple API calls are made if necessary, based on the `max_comments` value and the number of comments available.

## Limitations

- The YouTube API has usage quotas and limits. Be mindful of how frequently you're making requests, especially when fetching a large number of comments.
- Each API call can fetch a maximum of 100 comments, so requesting more than 100 comments will result in multiple API calls.
- Fetching a very large number of comments may take a considerable amount of time and could potentially hit API quotas.

## Extension Configuration

You can use the following YAML configuration to create this extension in your application:

```yaml
name: YouTube Comments Fetcher
description: Fetches comments from a specified YouTube video using the Google API
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/youtube-commentsfetcher
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: video-id
      name: Video ID
      description: The ID of the YouTube video to fetch comments from
      key: video_id
      type: string
      required: true
    - id: auth-token
      name: Auth Token
      description: Your Google API key or OAuth token for authentication
      key: auth_token
      type: string
      required: true
    - id: is-oauth
      name: Is OAuth
      description: Set to true if using an OAuth token instead of an API key
      key: is_oauth
      type: boolean
      required: false
    - id: max-comments
      name: Max Comments
      description: The maximum number of comments to fetch (default is 100)
      key: max_comments
      type: number
      required: false
  outputs:
    - id: comments
      name: Comments
      description: An array containing the fetched comments from the specified video
      key: comments
      type: string
    - id: video-id
      name: Video ID
      description: The ID of the video that was processed (echoed from input)
      key: video_id
      type: string
    - id: total-results
      name: Total Results
      description: The total number of comments fetched
      key: total_results
      type: number
```

To use this configuration:

1. Copy the YAML content above.
2. In your application's YAML/JSON editor, paste the configuration.
3. Adjust any fields as necessary to match your specific requirements.

This configuration sets up the extension with the correct inputs and outputs, resource requests, and other necessary metadata. The `visibility` is set to `private`, but you can change this to `public` if you want the extension to be publicly available.

## Customization

You can customize this extension further by:
- Adding more metadata about the video in the output
- Implementing comment filtering based on certain criteria
- Adding support for fetching replies to comments (requires additional API calls)

## Troubleshooting

If you encounter issues:

1. Ensure your Google API key is valid and has the YouTube Data API v3 enabled.
2. Check if you've exceeded your API quota for the day.
3. Verify that the video ID is correct and the video is publicly accessible.
4. Check the extension logs for any error messages or warnings.
5. If using OAuth, ensure that your token includes the required `youtube.force-ssl` scope. Which is full access to youtube.

## Updates and Maintenance

This extension is maintained by the OrchestrateAI team. For bug reports, feature requests, or contributions, please open an issue or pull request in the GitHub repository.
