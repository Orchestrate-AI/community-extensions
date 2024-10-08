const dotenv = require('dotenv');
const redis = require('redis');
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
  await publisher.connect();
  await subscriber.connect();

  await publisher.publish(REDIS_CHANNEL_READY, '');

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
      const errorOutput = {
        type: 'failed',
        workflowInstanceId: WORKFLOW_INSTANCE_ID,
        workflowExtensionId: WORKFLOW_EXTENSION_ID,
        error: error.message
      };
      await publisher.publish(REDIS_CHANNEL_OUT, JSON.stringify(errorOutput));
    } finally {
      await subscriber.unsubscribe(REDIS_CHANNEL_IN);
      await subscriber.quit();
      await publisher.quit();
    }
  });
}

async function processMessage(message) {
  const { inputs } = JSON.parse(message);
  const { email, firstName, lastName, listId } = inputs;

  if (!email || !listId) {
    throw new Error('Email and listId are required');
  }

  const subscriberHash = mailchimp.md5(email.toLowerCase());

  try {
    const response = await mailchimp.lists.setListMember(listId, subscriberHash, {
      email_address: email,
      status_if_new: 'subscribed',
      merge_fields: {
        FNAME: firstName || '',
        LNAME: lastName || '',
      },
    });

    return {
      success: true,
      id: response.id,
      email: response.email_address,
      status: response.status,
    };
  } catch (error) {
    console.error('Error adding subscriber to MailChimp:', error);
    throw new Error('Failed to add subscriber to MailChimp');
  }
}

main().catch(console.error);