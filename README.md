# Community Extensions Repository

## Table of Contents
1. [Introduction](#introduction)
2. [Repository Structure](#repository-structure)
3. [Getting Started](#getting-started)
4. [Contributing](#contributing)
5. [Extension Guidelines](#extension-guidelines)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Support](#support)

## Introduction

Welcome to the Community Extensions Repository! This repository houses a collection of community-contributed extensions for our workflow system. Each extension is a modular unit of work that performs specific tasks within a larger workflow, communicating with the workflow engine via Redis channels.

## Repository Structure

The repository is organized as follows:

```
community-extensions/
├── extension-1/
│   ├── README.md
│   ├── main file (e.g., main.py, main.go, index.ts, Main.java)
│   ├── dependency file (e.g., requirements.txt, go.mod, package.json, pom.xml)
│   └── Dockerfile
├── extension-2/
│   ├── README.md
│   ├── main file
│   ├── dependency file
│   └── Dockerfile
├── ...
└── README.md (this file)
```

Each root folder represents a single extension and contains all necessary files for that extension.

## Getting Started

To use or contribute to an extension:

1. Clone this repository:
   ```
   git clone https://github.com/your-org/community-extensions.git
   cd community-extensions
   ```

2. Navigate to the specific extension folder you're interested in:
   ```
   cd extension-name
   ```

3. Follow the README.md file in the extension's folder for specific instructions on building, testing, and using that extension.

## Contributing

We welcome contributions from the community! To contribute:

1. Fork this repository.
2. Create a new folder for your extension with a descriptive name.
3. Develop your extension following the [Extension Guidelines](#extension-guidelines).
4. Create a pull request with your new extension or improvements to an existing one.

Please read our [CONTRIBUTING.md](.github/CONTRIBUTING.md) file for more detailed information on the contribution process.

## Extension Guidelines

When creating or modifying an extension, please adhere to these guidelines:

1. Each extension should be in its own root folder with a descriptive name.
2. Include a README.md file in your extension folder with:
   - A clear description of what the extension does
   - Requirements and dependencies
   - Build and run instructions
   - Usage examples
   - Any configuration options
   - The extension YAML definition (see example below)
3. Implement proper error handling and logging.
4. Ensure your extension is stateless or uses external storage for state.
5. Always return a JSON-serializable object from your message processing function.
6. Include a Dockerfile for containerization.
7. Follow best practices and idiomatic conventions for the language you're using.
8. Choose the most appropriate language for your extension. While we provide a JavaScript guide, you can use any language that best suits your extension's requirements and your expertise.
9. The following environment variables will be provided by the workflow engine and should be used for Redis communication:
   - WORKFLOW_INSTANCE_ID
   - WORKFLOW_EXTENSION_ID
   - REDIS_HOST_URL
   - REDIS_USERNAME
   - REDIS_PASSWORD
   - REDIS_CHANNEL_IN
   - REDIS_CHANNEL_OUT
   - REDIS_CHANNEL_READY
   These variables are set when the extension's container is created and remain constant throughout its lifecycle. They cannot be modified during runtime.
10. Any additional configuration or sensitive information (like API tokens) should be passed as part of the input message received on REDIS_CHANNEL_IN, not as environment variables.
11. Strictly follow the communication flow outlined in the extension-communication.md file. This flow is crucial for proper interaction with the workflow engine and Redis.

### Example Extension YAML Definition

Include a YAML configuration in your README.md that defines your extension. Here's an example:

```yaml
name: Your Extension Name
description: A brief description of what your extension does
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/your-extension-name
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: input-1
      name: Input 1 Name
      description: Description of input 1
      key: input_1_key
      type: string
      required: true
  outputs:
    - id: output-1
      name: Output 1 Name
      description: Description of output 1
      key: output_1_key
      type: string
```

Adjust the YAML configuration to match your extension's specific inputs, outputs, and resource requirements.

## Testing

Each extension should include its own tests. We recommend:

1. Unit tests for core logic
2. Integration tests that simulate Redis communication
3. Dockerfile tests to ensure proper containerization

Please run all tests locally before submitting a pull request.

## Deployment

Extensions in this repository are automatically built and deployed using a GitHub Action workflow. Here's how it works:

1. When changes are pushed to the `main` branch, the GitHub Action is triggered.
2. The action scans for directories containing Dockerfiles.
3. For each directory with changes, the action:
   - Builds a Docker image for the extension.
   - Tags the image with `latest` and the current commit SHA.
   - Pushes the image to the GitHub Container Registry (ghcr.io).


To use an extension in your workflow:

1. Reference the extension in your workflow configuration using the automatically built image.
2. The image URL will be in the format: `ghcr.io/orchestrate-ai/<extension-name>:latest`
   and `ghcr.io/orchestrate-ai/<extension-name>:<commit-sha>` for a specific version.

For example:
```yaml
name: <extension-name>
description: <description>
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/<extension-name>
  dockerTag: latest
```

Note: Ensure your workflow system has the necessary permissions to pull images from the GitHub Container Registry.

### Manual Deployment

If you need to deploy an extension manually:

1. Navigate to the extension's directory.
2. Build the Docker image locally:
   ```
   docker build -t my-extension .
   ```
3. Tag the image with your registry's URL:
   ```
   docker tag my-extension:latest your-registry.com/my-extension:latest
   ```
4. Push the image to your registry:
   ```
   docker push your-registry.com/my-extension:latest
   ```
5. Reference the extension in your configuration, specifying the Docker image and tag.

## Support

For questions or issues related to specific extensions, please open an issue in this repository, tagging it with the extension name.

Thank you for your interest in our Community Extensions! We look forward to seeing what you create.
