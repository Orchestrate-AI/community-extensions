const redis = require('redis');
const axios = require('axios');

const {
  WORKFLOW_INSTANCE_ID,
  WORKFLOW_EXTENSION_ID,
  REDIS_HOST_URL,
  REDIS_USERNAME,
  REDIS_PASSWORD,
  REDIS_CHANNEL_IN,
  REDIS_CHANNEL_OUT,
  REDIS_CHANNEL_READY
} = process.env;

const publisher = redis.createClient({
  url: REDIS_HOST_URL,
  username: REDIS_USERNAME,
  password: REDIS_PASSWORD,
});

const subscriber = redis.createClient({
  url: REDIS_HOST_URL,
  username: REDIS_USERNAME,
  password: REDIS_PASSWORD,
});

async function main() {
  await publisher.connect();
  await subscriber.connect();

  await subscriber.subscribe(REDIS_CHANNEL_IN, async (message) => {
    const result = await processMessage(message);
    await publisher.publish(REDIS_CHANNEL_OUT, JSON.stringify(result));
  });

  await publisher.publish(REDIS_CHANNEL_READY, '');
}

async function processMessage(message) {
  try {
    const { inputs } = JSON.parse(message);
    const { shopDomain, accessToken, productId } = inputs;

    if (!shopDomain || !accessToken || !productId) {
      throw new Error('Missing required inputs: shopDomain, accessToken, or productId');
    }

    const shopifyApiUrl = `https://${shopDomain}/admin/api/2023-07/products/${productId}/variants.json`;

    const response = await axios.get(shopifyApiUrl, {
      headers: {
        'X-Shopify-Access-Token': accessToken,
        'Content-Type': 'application/json'
      }
    });

    const variants = response.data.variants;
    const inventoryLevels = variants.map(variant => ({
      variantId: variant.id,
      inventoryQuantity: variant.inventory_quantity
    }));

    return {
      type: 'completed',
      workflowInstanceId: WORKFLOW_INSTANCE_ID,
      workflowExtensionId: WORKFLOW_EXTENSION_ID,
      output: {
        inventoryLevels,
        timestamp: new Date().toISOString()
      }
    };
  } catch (error) {
    return {
      type: 'failed',
      workflowInstanceId: WORKFLOW_INSTANCE_ID,
      workflowExtensionId: WORKFLOW_EXTENSION_ID,
      error: error.message
    };
  }
}

main().catch(console.error);