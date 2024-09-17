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

## Updates and Maintenance

This extension is maintained by the community. For bug reports, feature requests, or contributions, please open an issue or pull request in the GitHub repository.

## Usage Examples

Here's an example of how to use the YouTube Comments Fetcher Extension with an API key:

```yaml
extensions:
  - name: youtube-comments-fetcher
    image: ghcr.io/your-org/youtube-comments-fetcher:latest
    inputs:
      video_id: "dQw4w9WgXcQ"
      auth_token: "YOUR_GOOGLE_API_KEY"
      max_comments: 50
```

And here's an example using an OAuth token:

```yaml
extensions:
  - name: youtube-comments-fetcher
    image: ghcr.io/your-org/youtube-comments-fetcher:latest
    inputs:
      video_id: "dQw4w9WgXcQ"
      auth_token: "YOUR_OAUTH_TOKEN"
      is_oauth: true
      max_comments: 50
```

Make sure to replace "YOUR_GOOGLE_API_KEY" or "YOUR_OAUTH_TOKEN" with your actual authentication credentials.
