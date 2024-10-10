# Shopify-GetProductInventoryLevels

This extension retrieves the inventory levels for a specific product in a Shopify store using the Shopify Admin API.

## Description

The extension connects to a Shopify store, fetches variant information for a given product ID, and returns the inventory quantity for each variant.

## Requirements

- Node.js 18 LTS
- Redis
- Shopify store with Admin API access

## Usage

This extension is designed to be used within a workflow system that provides necessary environment variables and handles Redis communication.

### Inputs

The extension expects the following inputs in the message received on REDIS_CHANNEL_IN:

- `shopDomain`: The domain of the Shopify store (e.g., "your-store.myshopify.com")
- `accessToken`: The Shopify Admin API access token
- `productId`: The ID of the product to fetch inventory levels for

### Outputs

The extension will publish a message to REDIS_CHANNEL_OUT with the following structure:

```json
{
  "type": "completed",
  "workflowInstanceId": "<workflow_instance_id>",
  "workflowExtensionId": "<workflow_extension_id>",
  "output": {
    "inventoryLevels": [
      {
        "variantId": "<variant_id>",
        "inventoryQuantity": <quantity>
      },
      ...
    ],
    "timestamp": "<ISO8601_timestamp>"
  }
}
```

In case of an error, the output will have the following structure:

```json
{
  "type": "failed",
  "workflowInstanceId": "<workflow_instance_id>",
  "workflowExtensionId": "<workflow_extension_id>",
  "error": "<error_message>"
}
```

## Environment Variables

The extension uses the following environment variables provided by the workflow engine:

- WORKFLOW_INSTANCE_ID
- WORKFLOW_EXTENSION_ID
- REDIS_HOST_URL
- REDIS_USERNAME
- REDIS_PASSWORD
- REDIS_CHANNEL_IN
- REDIS_CHANNEL_OUT
- REDIS_CHANNEL_READY

## Building and Deployment

1. Build the Docker image:
   ```
   docker build -t shopify-get-product-inventory-levels .
   ```

2. Push the image to your container registry.

3. Use the image in your workflow configuration:

```yaml
name: Shopify-GetProductInventoryLevels
description: Retrieves inventory levels for a specific product in a Shopify store
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/shopify-get-product-inventory-levels
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: shopDomain
      name: Shopify Store Domain
      description: The domain of the Shopify store
      key: shopDomain
      type: string
      required: true
    - id: accessToken
      name: Access Token
      description: Shopify Admin API access token
      key: accessToken
      type: string
      required: true
    - id: productId
      name: Product ID
      description: ID of the product to fetch inventory levels for
      key: productId
      type: string
      required: true
  outputs:
    - id: inventoryLevels
      name: Inventory Levels
      description: Inventory levels for the product variants
      key: inventoryLevels
      type: array
```

Ensure that your workflow system has the necessary permissions to pull the image from the container registry.