# Shopify-GetProductInventoryLevels Extension

This extension retrieves product inventory levels from Shopify using the Shopify Admin API.

## Requirements

- Python 3.9 or later
- Docker (for containerized deployment)

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

This extension is designed to be run as part of a workflow system. It communicates via Redis channels and expects certain environment variables to be set.

### Input

The extension expects the following inputs in the message received on the REDIS_CHANNEL_IN:

- `shop_url`: The URL of the Shopify shop (e.g., "https://your-shop.myshopify.com")
- `access_token`: The Shopify Admin API access token
- `inventory_item_ids`: Comma-separated list of inventory item IDs
- `location_ids`: Comma-separated list of location IDs

### Output

The extension will publish the result to REDIS_CHANNEL_OUT. The output will be a JSON object with the following structure:

```json
{
  "success": true,
  "inventory_levels": {
    "inventory_levels": [
      {
        "inventory_item_id": 39072856,
        "location_id": 487838322,
        "available": 27,
        "updated_at": "2023-06-14T15:30:00-04:00",
        "admin_graphql_api_id": "gid://shopify/InventoryLevel/487838322?inventory_item_id=39072856"
      },
      ...
    ]
  }
}
```

In case of an error, the output will have the following structure:

```json
{
  "success": false,
  "error": "Error message"
}
```

## Development

To run the extension locally for development:

1. Set up a local Redis instance
2. Set the required environment variables (WORKFLOW_INSTANCE_ID, WORKFLOW_EXTENSION_ID, REDIS_HOST_URL, etc.)
3. Run the script: `python main.py`

## Deployment

To deploy this extension:

1. Build the Docker image:
   ```
   docker build -t shopify-get-inventory-levels .
   ```
2. Push the image to your container registry
3. Configure your workflow system to use this image, providing the necessary environment variables and Redis connection details

## License

[MIT License](https://opensource.org/licenses/MIT)