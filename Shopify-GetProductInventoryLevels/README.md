# Shopify-GetProductInventoryLevels

This extension retrieves product inventory levels from a Shopify store using the Shopify API.

## Requirements

- Python 3.9+
- Redis
- Shopify API access

## Configuration

The following environment variables are required:

- WORKFLOW_INSTANCE_ID
- WORKFLOW_EXTENSION_ID
- REDIS_HOST_URL
- REDIS_USERNAME
- REDIS_PASSWORD
- REDIS_CHANNEL_IN
- REDIS_CHANNEL_OUT
- REDIS_CHANNEL_READY

## Input

The extension expects the following input:

```json
{
  "shop_url": "your-store.myshopify.com",
  "access_token": "your_shopify_access_token"
}
```

## Output

The extension returns the inventory levels in the following format:

```json
{
  "inventory_levels": [
    {
      "inventory_item_id": 123456789,
      "location_id": 987654321,
      "available": 10,
      "updated_at": "2023-05-20T12:00:00Z"
    },
    ...
  ]
}
```

If an error occurs, the output will be:

```json
{
  "error": "Error message"
}
```

## Features

- Retrieves all inventory levels, handling pagination automatically
- Implements error handling for common API issues (authentication, rate limiting)
- Logs important events and errors for monitoring and debugging

## Building and Running

1. Build the Docker image:
   ```
   docker build -t shopify-get-product-inventory-levels .
   ```

2. Run the container:
   ```
   docker run -e WORKFLOW_INSTANCE_ID=... -e WORKFLOW_EXTENSION_ID=... -e REDIS_HOST_URL=... -e REDIS_USERNAME=... -e REDIS_PASSWORD=... -e REDIS_CHANNEL_IN=... -e REDIS_CHANNEL_OUT=... -e REDIS_CHANNEL_READY=... shopify-get-product-inventory-levels
   ```

## Extension YAML Definition

```yaml
name: Shopify-GetProductInventoryLevels
description: Retrieves product inventory levels from a Shopify store
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/shopify-get-product-inventory-levels
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: shop_url
      name: Shop URL
      description: The URL of your Shopify store
      key: shop_url
      type: string
      required: true
    - id: access_token
      name: Access Token
      description: Your Shopify API access token
      key: access_token
      type: string
      required: true
  outputs:
    - id: inventory_levels
      name: Inventory Levels
      description: List of inventory levels for products
      key: inventory_levels
      type: array
    - id: error
      name: Error
      description: Error message if an error occurred
      key: error
      type: string
```

## Security Considerations

- Ensure that the Shopify access token is kept secure and not exposed in logs or error messages.
- Use HTTPS for all API communications.
- Regularly rotate the Shopify access token.

## Limitations

- The extension does not implement advanced rate limiting strategies. For high-volume use, consider implementing more sophisticated rate limiting.
- Error handling is basic. For production use, consider implementing more detailed error reporting and recovery strategies.

## Testing

To ensure the reliability of this extension, implement the following tests:

1. Unit tests for the `get_inventory_levels` function, mocking the API responses.
2. Integration tests with a test Shopify store to verify real-world behavior.
3. Error handling tests to ensure proper handling of various error conditions.
4. Performance tests to verify behavior with large datasets.

## Monitoring and Logging

The extension logs important events and errors. For production use, consider implementing more advanced logging and monitoring solutions to track the extension's performance and detect issues proactively.