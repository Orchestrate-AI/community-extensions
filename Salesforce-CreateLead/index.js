const jsforce = require('jsforce');
const redis = require('redis');
const console = require('console');

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

  await publisher.publish(REDIS_CHANNEL_READY, '');

  await subscriber.subscribe(REDIS_CHANNEL_IN, async (message) => {
    const result = await processMessage(message);

    const output = {
      type: 'completed',
      workflowInstanceId: WORKFLOW_INSTANCE_ID,
      workflowExtensionId: WORKFLOW_EXTENSION_ID,
      output: result
    };
    await publisher.publish(REDIS_CHANNEL_OUT, JSON.stringify(output));

    await subscriber.unsubscribe(REDIS_CHANNEL_IN);
    await subscriber.quit();
    await publisher.quit();
  });
}

function validateInputs(inputs) {
  const requiredFields = ['firstName', 'lastName', 'company', 'email', 'username', 'password'];
  for (const field of requiredFields) {
    if (!inputs[field]) {
      throw new Error(`Missing required field: ${field}`);
    }
  }
}

async function processMessage(message) {
  const { inputs } = JSON.parse(message);
  let conn;
  
  try {
    validateInputs(inputs);

    conn = new jsforce.Connection({
      loginUrl: inputs.loginUrl || 'https://login.salesforce.com'
    });

    console.log(`Attempting to login to Salesforce as ${inputs.username}`);
    await conn.login(inputs.username, inputs.password);
    console.log('Successfully logged in to Salesforce');

    const lead = {
      FirstName: inputs.firstName,
      LastName: inputs.lastName,
      Company: inputs.company,
      Email: inputs.email,
      Phone: inputs.phone
    };

    console.log(`Attempting to create lead for ${inputs.firstName} ${inputs.lastName}`);
    const result = await conn.sobject('Lead').create(lead);
    console.log(`Lead creation result: ${JSON.stringify(result)}`);

    return {
      success: result.success,
      id: result.id,
      errors: result.errors
    };
  } catch (error) {
    console.error(`Error occurred: ${error.message}`);
    return {
      success: false,
      error: error.message
    };
  } finally {
    if (conn) {
      console.log('Logging out from Salesforce');
      await conn.logout();
    }
  }
}

main().catch(console.error);