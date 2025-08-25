const redis = require('redis');
const winston = require('winston');
const envalid = require('envalid');

const env = envalid.cleanEnv(process.env, {
  WORKFLOW_INSTANCE_ID: envalid.str(),
  WORKFLOW_EXTENSION_ID: envalid.str(),
  REDIS_HOST_URL: envalid.str(),
  REDIS_USERNAME: envalid.str(),
  REDIS_PASSWORD: envalid.str(),
  REDIS_CHANNEL_IN: envalid.str(),
  REDIS_CHANNEL_OUT: envalid.str(),
  REDIS_CHANNEL_READY: envalid.str(),
});

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'generic-processdata' },
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

const publisher = redis.createClient({
  url: env.REDIS_HOST_URL,
  username: env.REDIS_USERNAME,
  password: env.REDIS_PASSWORD,
});

const subscriber = redis.createClient({
  url: env.REDIS_HOST_URL,
  username: env.REDIS_USERNAME,
  password: env.REDIS_PASSWORD,
});

async function main() {
  try {
    await publisher.connect();
    await subscriber.connect();

    await subscriber.subscribe(env.REDIS_CHANNEL_IN, async (message) => {
      try {
        const result = await processMessage(message);
        await publisher.publish(env.REDIS_CHANNEL_READY, '');

        const output = {
          type: 'completed',
          workflowInstanceId: env.WORKFLOW_INSTANCE_ID,
          workflowExtensionId: env.WORKFLOW_EXTENSION_ID,
          output: result
        };
        await publisher.publish(env.REDIS_CHANNEL_OUT, JSON.stringify(output));
      } catch (error) {
        logger.error('Error processing message:', error);
        const errorOutput = {
          type: 'failed',
          workflowInstanceId: env.WORKFLOW_INSTANCE_ID,
          workflowExtensionId: env.WORKFLOW_EXTENSION_ID,
          error: error.message
        };
        await publisher.publish(env.REDIS_CHANNEL_OUT, JSON.stringify(errorOutput));
      } finally {
        await subscriber.unsubscribe(env.REDIS_CHANNEL_IN);
        await subscriber.quit();
        await publisher.quit();
      }
    });

    logger.info('Generic-ProcessData extension is ready and listening for messages.');
  } catch (error) {
    logger.error('Error in main function:', error);
    process.exit(1);
  }
}

async function processMessage(message) {
  const { inputs } = JSON.parse(message);
  
  if (!inputs || !inputs.data) {
    throw new Error('Invalid input: missing data');
  }

  // Simple processing: reverse the input string
  const reversedInput = inputs.data.split('').reverse().join('');

  logger.info('Processed input successfully');

  return {
    result: reversedInput,
    timestamp: new Date().toISOString()
  };
}

// Health check endpoint
const http = require('http');
const server = http.createServer((req, res) => {
  if (req.url === '/health' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'healthy' }));
  } else {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not Found' }));
  }
});

server.listen(3000, () => {
  logger.info('Health check server running on port 3000');
});

main();