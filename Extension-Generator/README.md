# Extension Generator

## Description

The Extension Generator is an automated tool designed to create new extensions for the OrchestrateAI workflow system. It uses AI-powered agents to generate, validate, and optimize extension code based on a given specification.

## Features

- Automated extension creation based on user-provided specifications
- AI-powered code generation using GPT-4 and Claude models
- Automatic validation of generated code against community guidelines
- Library version checking to ensure up-to-date dependencies
- Automatic creation of a new branch and pull request in the community-extensions repository

## Requirements

- Python 3.11+
- Docker (for containerized deployment)
- Access to OpenAI, Anthropic, and Serper API keys
- GitHub App credentials (for repository interactions)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Orchestrate-AI/community-extensions.git
   cd community-extensions/Extension-Generator
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

The Extension Generator is designed to be run as part of the OrchestrateAI workflow system. It receives input via a Redis channel and publishes its output to another Redis channel.

### Input Format

The extension expects input in the following format:

```json
{
  "inputs": {
    "extension_spec": "<Service,Description,Action>",
    "github_app_id": "your-github-app-id",
    "github_private_key": "your-github-private-key",
    "openai_api_key": "your-openai-api-key",
    "anthropic_api_key": "your-anthropic-api-key",
    "serper_api_key": "your-serper-api-key",
    "ideator_model": "claude",
    "developer_model": "claude",
    "documenter_model": "claude",
    "reviewer_model": "claude"
  }
}
```

### Output Format

The extension produces output in the following format:

```json
{
  "type": "completed",
  "workflowInstanceId": "instance-id",
  "workflowExtensionId": "extension-id",
  "output": {
    "status": "success",
    "result": {
      "new_branch": "new-extension-branch-name",
      "pr_url": "https://github.com/Orchestrate-AI/community-extensions/pull/123"
    }
  }
}
```

## Configuration

The extension uses the following environment variables:

- `WORKFLOW_INSTANCE_ID`
- `WORKFLOW_EXTENSION_ID`
- `REDIS_HOST_URL`
- `REDIS_USERNAME`
- `REDIS_PASSWORD`
- `REDIS_CHANNEL_IN`
- `REDIS_CHANNEL_OUT`
- `REDIS_CHANNEL_READY`

These are automatically set by the OrchestrateAI workflow engine.

## Development

To run the extension locally for development or testing:

1. Set up the required environment variables in a `.env` file.
2. Run the extension:
   ```
   python main.py
   ```

For end-to-end testing, you can use the provided `e2e_test.py` script:

```
python e2e_test.py
```

## Docker

To build and run the Docker container:

```
docker build -t extension-generator .
docker run --env-file .env extension-generator
```

## Contributing

Contributions to improve the Extension Generator are welcome. Please follow the standard GitHub pull request process to submit your changes.

## License

[MIT License](LICENSE)