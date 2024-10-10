# Shopify - Get Product Inventory Levels

This extension retrieves product inventory levels from Shopify using the Shopify Admin API. It accepts a list of product IDs, fetches their variants, and then retrieves the inventory levels for those variants across all locations.

## Requirements

- Python 3.8
- aiohttp
- aioredis

## Configuration

The extension requires the following environment variables:

- WORKFLOW_INSTANCE_ID
- WORKFLOW_EXTENSION_ID
- REDIS_HOST_URL
- REDIS_USERNAME
- REDIS_PASSWORD
- REDIS_CHANNEL_IN
- REDIS_CHANNEL_OUT
- REDIS_CHANNEL_READY

These are provided by the workflow engine when the extension is run.

## Input

The extension expects an input message with the following structure:

```json
{
  "inputs": {
    "product_ids": ["1234567890", "0987654321"],
    "shop_name": "your-shop-name",
    "access_token": "your-access-token"
  }
}
```

- `product_ids`: An array of Shopify product IDs to fetch inventory levels for.
- `shop_name`: Your Shopify shop name (e.g., if your shop URL is `myshop.myshopify.com`, the shop name is `myshop`).
- `access_token`: Your Shopify Admin API access token.

## Output

The extension will return an output message with the following structure:

```json
{
  "inventory_levels": [
    {
      "inventory_item_id": 39072856,
      "location_id": 655441491,
      "available": 40,
      "updated_at": "2023-05-30T15:00:00-04:00",
      "admin_graphql_api_id": "gid://shopify/InventoryLevel/655441491?inventory_item_id=39072856"
    },
    // ... more inventory levels
  ]
}
```

If an error occurs, the output will contain an error message:

```json
{
  "error": "Error message details"
}
```

## Building and Running

1. Build the Docker image:
   ```
   docker build -t shopify-get-product-inventory-levels .
   ```

2. Run the container:
   ```
   docker run -e WORKFLOW_INSTANCE_ID=<value> -e WORKFLOW_EXTENSION_ID=<value> -e REDIS_HOST_URL=<value> -e REDIS_USERNAME=<value> -e REDIS_PASSWORD=<value> -e REDIS_CHANNEL_IN=<value> -e REDIS_CHANNEL_OUT=<value> -e REDIS_CHANNEL_READY=<value> shopify-get-product-inventory-levels
   ```

Replace `<value>` with the appropriate values for each environment variable.

## Notes

- This extension uses asynchronous programming with `aiohttp` for efficient API requests and `aioredis` for Redis communication.
- Make sure your Shopify API access token has the necessary permissions to read inventory information.
- The extension automatically handles pagination for product variants but assumes the number of inventory levels returned is within Shopify's limit (250). If you need to handle more inventory levels, you may need to implement pagination for the inventory levels request as well.

```yaml
name: Shopify - Get Product Inventory Levels
description: Retrieves product inventory levels from Shopify using the Shopify Admin API
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/shopify-get-product-inventory-levels
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: product-ids
      name: Product IDs
      description: List of Shopify product IDs to fetch inventory levels for
      key: product_ids
      type: array
      required: true
    - id: shop-name
      name: Shopify Shop Name
      description: Your Shopify shop name (e.g., if your shop URL is myshop.myshopify.com, the shop name is myshop)
      key: shop_name
      type: string
      required: true
    - id: access-token
      name: Shopify Access Token
      description: Your Shopify Admin API access token
      key: access_token
      type: string
      required: true
  outputs:
    - id: inventory-levels
      name: Inventory Levels
      description: List of inventory levels for the requested products
      key: inventory_levels
      type: array
```