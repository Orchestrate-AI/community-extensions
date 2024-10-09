const redis = require('redis');
const dotenv = require('dotenv');
const mailchimp = require('@mailchimp/mailchimp_marketing');

dotenv.config();

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
  MAILCHIMP_SERVER_PREFIX
} = process.env;

// Validate required environment variables
const requiredEnvVars = [
  'WORKFLOW_INSTANCE_ID',
  'WORKFLOW_EXTENSION_ID',
  'REDIS_HOST_URL',
  'REDIS_CHANNEL_IN',
  'REDIS_CHANNEL_OUT',
  'REDIS_CHANNEL_READY',
  'MAILCHIMP_API_KEY',
  'MAILCHIMP_SERVER_PREFIX'
];

requiredEnvVars.forEach(varName => {
  if (!process.env[varName]) {
    throw new Error(`Missing required environment variable: ${varName}`);
  }
});

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

mailchimp.setConfig({
  apiKey: MAILCHIMP_API_KEY,
  server: MAILCHIMP_SERVER_PREFIX,
});

async function main() {
  try {
    await publisher.connect();
    await subscriber.connect();

    console.log('Connected to Redis');

    await publisher.publish(REDIS_CHANNEL_READY, '');
    console.log('Published ready message');

    await subscriber.subscribe(REDIS_CHANNEL_IN, async (message) => {
      try {
        console.log('Received message:', message);
        const result = await processMessage(message);

        const output = {
          type: 'completed',
          workflowInstanceId: WORKFLOW_INSTANCE_ID,
          workflowExtensionId: WORKFLOW_EXTENSION_ID,
          output: result
        };
        await publisher.publish(REDIS_CHANNEL_OUT, JSON.stringify(output));
        console.log('Published result:', output);
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
    });
  } catch (error) {
    console.error('Error in main function:', error);
    process.exit(1);
  }
}

async function processMessage(message) {
  const { inputs } = JSON.parse(message);
  const { email, firstName, lastName, listId } = inputs;

  if (!email || !listId) {
    throw new Error('Email and listId are required');
  }

  if (!validateEmail(email)) {
    throw new Error('Invalid email format');
  }

  const subscriberData = {
    email_address: email,
    status: 'subscribed',
    merge_fields: {
      FNAME: firstName || '',
      LNAME: lastName || ''
    }
  };

  try {
    const response = await mailchimp.lists.addListMember(listId, subscriberData);
    console.log('Subscriber added successfully:', response.id);
    return {
      id: response.id,
      email: response.email_address,
      status: response.status
    };
  } catch (error) {
    console.error('Error adding subscriber to MailChimp:', error);
    throw new Error(`Failed to add subscriber: ${error.message}`);
  }
}

function validateEmail(email) {
  const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return re.test(String(email).toLowerCase());
}

main().catch(console.error);

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received. Closing Redis connections...');
  await subscriber.quit();
  await publisher.quit();
  process.exit(0);
});