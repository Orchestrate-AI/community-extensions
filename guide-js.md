# Workflow Extension Development Guide (JavaScript)

## Table of Contents
1. [Introduction](#introduction)
2. [Requirements](#requirements)
3. [Getting Started](#getting-started)
4. [Extension Structure](#extension-structure)
5. [Message Schema](#message-schema)
6. [Developing Your Extension](#developing-your-extension)
7. [Building and Testing](#building-and-testing)
8. [Deployment](#deployment)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Introduction

This guide will walk you through the process of creating an extension. Extensions are modular units of work that perform specific tasks within a larger workflow. They are containerized applications that communicate with the workflow engine via Redis channels.

## Requirements

To create an extension, you'll need:

- Docker installed on your development machine
- Access to a Docker registry (e.g., Docker Hub)
- Node.js and npm (or another suitable runtime environment)
- Redis client library for your chosen programming language
- Basic understanding of Redis pub/sub mechanism
- Familiarity with containerization and environment variables

## Getting Started

1. Create a new directory for your extension:
   ```bash
   mkdir my-extension
   cd my-extension
   ```

2. Initialize your project:
   ```bash
   npm init -y
   ```

3. Install required dependencies:
   ```bash
   npm install redis dotenv
   ```

## Extension Structure

Your extension should have the following basic structure:

```
my-extension/
├── index.js
├── package.json
├── Dockerfile
└── .env (for local testing)
```

## Message Schema

Your extension will receive messages on the REDIS_CHANNEL_IN with the following schema:

```javascript
const message = {
  workflowExtensionId: string,
  workflowInstanceId: string,
  inputs: Record<string, any>
};
```

The `inputs` object will contain key-value pairs corresponding to the inputs defined in your extension's configuration.

## Developing Your Extension

1. Create an `index.js` file with the following structure:

```javascript
const redis = require('redis');
const dotenv = require('dotenv');

dotenv.config();

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

async function processMessage(message) {
  const { inputs } = JSON.parse(message);
  
  // Implement your extension's logic here
  // Process the inputs and generate a result

  // IMPORTANT: Always return a JSON object, even if it's empty
  return {
    result: `Processed inputs: ${JSON.stringify(inputs)}`,
    timestamp: new Date().toISOString()
  };
}

main().catch(console.error);
```

2. Implement your extension's logic in the `processMessage` function.

3. Create a `Dockerfile`:

```dockerfile
FROM node:14

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install

COPY . .

CMD [ "node", "index.js" ]
```

## Building and Testing

1. Build your Docker image:
   ```bash
   docker build -t my-extension .
   ```

2. Test locally by setting up a `.env` file with mock environment variables and running your extension.

## Deployment

1. Tag and push your image to a Docker registry:
   ```bash
   docker tag my-extension:latest your-registry/my-extension:latest
   docker push your-registry/my-extension:latest
   ```

2. Update the workflow configuration to include your new extension, specifying the Docker image and tag.

## Best Practices

1. **Error Handling**: Implement robust error handling. If an error occurs, publish an error message to REDIS_CHANNEL_OUT:

   ```javascript
   const errorOutput = {
     type: 'failed',
     workflowInstanceId: WORKFLOW_INSTANCE_ID,
     workflowExtensionId: WORKFLOW_EXTENSION_ID,
     error: 'Error message here'
   };
   await publisher.publish(REDIS_CHANNEL_OUT, JSON.stringify(errorOutput));
   ```

2. **Logging**: Use appropriate logging for debugging and monitoring.

3. **Configuration**: Use environment variables for configuration.

4. **Statelessness**: Design your extension to be stateless. Use Redis or another external storage for any necessary state.

5. **Performance**: Optimize for performance, especially if handling large data volumes.

6. **Return JSON**: Always return a JSON object from your `processMessage` function, even if it's empty. This ensures consistency in how the workflow engine handles your extension's output.

## Troubleshooting

- If your extension isn't receiving messages, check that the Redis connection details are correct.
- Ensure your Docker image is accessible to the Kubernetes cluster where the workflow engine runs.
- Check the logs of your extension's pod for any error messages or unexpected behavior.

Remember, the workflow engine provides all necessary environment variables when creating the pod for your extension. Your extension should be designed to read these variables and use them for Redis communication.