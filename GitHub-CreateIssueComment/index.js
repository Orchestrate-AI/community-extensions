const redis = require('redis');
const { Octokit } = require('@octokit/rest');
const { validate } = require('jsonschema');

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

const REDIS_TIMEOUT = 60000; // 60 seconds timeout

const inputSchema = {
  type: 'object',
  properties: {
    github_token: { type: 'string' },
    owner: { type: 'string' },
    repo: { type: 'string' },
    issue_number: { type: 'integer' },
    comment: { type: 'string' }
  },
  required: ['github_token', 'owner', 'repo', 'issue_number', 'comment']
};

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
  try {
    await publisher.connect();
    await subscriber.connect();

    console.log('Connected to Redis');

    await publisher.publish(REDIS_CHANNEL_READY, '');
    console.log('Published ready message');

    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Redis subscription timeout')), REDIS_TIMEOUT)
    );

    const subscriptionPromise = new Promise(async (resolve) => {
      await subscriber.subscribe(REDIS_CHANNEL_IN, async (message) => {
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

        resolve();
      });
    });

    await Promise.race([subscriptionPromise, timeoutPromise]);

    await subscriber.unsubscribe(REDIS_CHANNEL_IN);
    await subscriber.quit();
    await publisher.quit();
  } catch (error) {
    console.error('Error in main function:', error);
    console.error(error.stack);
    process.exit(1);
  }
}

async function processMessage(message) {
  try {
    const { inputs } = JSON.parse(message);
    const validationResult = validate(inputs, inputSchema);

    if (!validationResult.valid) {
      throw new Error(`Invalid input: ${validationResult.errors.map(e => e.stack).join(', ')}`);
    }

    const { github_token, owner, repo, issue_number, comment } = inputs;

    const octokit = new Octokit({ auth: github_token });

    const response = await octokit.issues.createComment({
      owner,
      repo,
      issue_number,
      body: comment
    });

    return {
      success: true,
      comment_id: response.data.id,
      comment_url: response.data.html_url
    };
  } catch (error) {
    console.error('Error processing message:', error);
    console.error(error.stack);
    return {
      success: false,
      error: error.message
    };
  }
}

main().catch(console.error);