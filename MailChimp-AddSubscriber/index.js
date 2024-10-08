const redis = require('redis');
const axios = require('axios');
const crypto = require('crypto');
const { promisify } = require('util');

const {
  WORKFLOW_INSTANCE_ID,
  WORKFLOW_EXTENSION_ID,
  REDIS_HOST_URL,
  REDIS_USERNAME,
  REDIS_PASSWORD,
  REDIS_CHANNEL_IN,
  REDIS_CHANNEL_OUT,
  REDIS_CHANNEL_READY,
  MAILCHIMP_API_KEY,
  MAILCHIMP_LIST_ID,
  MAILCHIMP_SERVER_PREFIX
} = process.env;

// Validate required environment variables
const requiredEnvVars = ['MAILCHIMP_API_KEY', 'MAILCHIMP_LIST_ID', 'MAILCHIMP_SERVER_PREFIX'];
requiredEnvVars.forEach(varName => {
  if (!process.env[varName]) {
    throw new Error(`Missing required environment variable: ${varName}`);
  }
});

// Validate MAILCHIMP_SERVER_PREFIX format
if (!/^[a-z]{2}\d+$/.test(MAILCHIMP_SERVER_PREFIX)) {
  throw new Error('Invalid MAILCHIMP_SERVER_PREFIX format. It should be in the format of "us1", "eu2", etc.');
}

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

const sleep = promisify(setTimeout);

async function main() {
  try {
    await publisher.connect();
    await subscriber.connect();

    console.log('Connected to Redis');

    await publisher.publish(REDIS_CHANNEL_READY, '');
    console.log('Published ready message');

    await subscriber.subscribe(REDIS_CHANNEL_IN, async (message) => {
      try {
        const result = await processMessage(message);
        const output = {
          type: 'completed',
          workflowInstanceId: WORKFLOW_INSTANCE_ID,
          workflowExtensionId: WORKFLOW_EXTENSION_ID,
          output: result
        };
        await publisher.publish(REDIS_CHANNEL_OUT, JSON.stringify(output));
      } catch (error) {
        console.error('Error processing message:', error);
        const errorOutput = {
          type: 'failed',
          workflowInstanceId: WORKFLOW_INSTANCE_ID,
          workflowExtensionId: WORKFLOW_EXTENSION_ID,
          error: error.message
        };
        await publisher.publish(REDIS_CHANNEL_OUT, JSON.stringify(errorOutput));
      }

      await subscriber.unsubscribe(REDIS_CHANNEL_IN);
      await subscriber.quit();
      await publisher.quit();
    });
  } catch (error) {
    console.error('Error in main function:', error);
    process.exit(1);
  }
}

async function processMessage(message) {
  const { inputs } = JSON.parse(message);
  const { email, ...mergeFields } = inputs;

  if (!email) {
    throw new Error('Email is required');
  }

  if (!isValidEmail(email)) {
    throw new Error('Invalid email format');
  }

  const subscriberHash = crypto.createHash('md5').update(email.toLowerCase()).digest('hex');

  const apiUrl = `https://${MAILCHIMP_SERVER_PREFIX}.api.mailchimp.com/3.0/lists/${MAILCHIMP_LIST_ID}/members/${subscriberHash}`;

  const data = {
    email_address: email,
    status: 'subscribed',
    merge_fields: mergeFields
  };

  try {
    const response = await axios.put(apiUrl, data, {
      auth: {
        username: 'anystring',
        password: MAILCHIMP_API_KEY
      },
      timeout: 5000 // 5 seconds timeout
    });

    return {
      status: 'success',
      message: 'Subscriber added successfully',
      subscriberId: response.data.id
    };
  } catch (error) {
    console.error('Error adding subscriber:', error.response?.data || error.message);
    throw new Error(`Failed to add subscriber: ${error.response?.data?.detail || error.message}`);
  }
}

function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Health check endpoint
const http = require('http');
http.createServer((req, res) => {
  if (req.url === '/health' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'healthy' }));
  } else {
    res.writeHead(404);
    res.end();
  }
}).listen(8080);

main().catch(console.error);