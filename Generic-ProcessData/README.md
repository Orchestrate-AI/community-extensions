# Generic-ProcessData Extension

This is a generic extension for processing data in a workflow. It demonstrates the basic structure and communication flow for a workflow extension, including Redis communication and simple data processing.

## Features

- Redis communication for workflow integration
- Simple data processing (string reversal)
- Logging with Winston
- Environment variable validation with Envalid
- Health check endpoint
- Containerized with Docker

## Prerequisites

- Node.js 18.x or later
- Redis server
- Docker (for containerized deployment)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/generic-processdata.git
   cd generic-processdata
   ```

2. Install dependencies:
   ```
   npm install
   ```

## Configuration

Set the following environment variables:

- WORKFLOW_INSTANCE_ID
- WORKFLOW_EXTENSION_ID
- REDIS_HOST_URL
- REDIS_USERNAME
- REDIS_PASSWORD
- REDIS_CHANNEL_IN
- REDIS_CHANNEL_OUT
- REDIS_CHANNEL_READY

## Usage

To run the extension locally:

```
npm start
```

To run tests:

```
npm test
```

## Docker Deployment

To build and run the Docker container:

```
docker build -t generic-processdata .
docker run -p 3000:3000 --env-file .env generic-processdata
```

## Health Check

The extension exposes a health check endpoint at `http://localhost:3000/health`.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the ISC License - see the [LICENSE.md](LICENSE.md) file for details.