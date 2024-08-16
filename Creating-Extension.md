# How to Create an Extension on OrchestrateAI

Extensions are powerful tools that allow you to expand the functionality of workflows. This guide will walk you through the process of creating your own extension using our user-friendly interface.

## Getting Started

1. Navigate to the extension creation page on our platform.
2. You'll see a form with several sections for configuring your extension.

## Basic Information

Start by providing the fundamental details of your extension:

1. **Name**: Enter a clear, descriptive name for your extension.
2. **Description**: Write a concise explanation of what your extension does and its purpose.
3. **Extension Type**: For this guide, we'll focus on 'container' type extensions.
4. **Visibility**: Choose between 'private' (only visible to you) or 'public' (visible to all users).

## Docker Configuration

Specify the Docker image for your extension:

1. **Docker Image**: Enter the address of your Docker image.
2. **Docker Tag**: Provide the specific tag for the image version you want to use.

## Resource Configuration

Define the computational resources your extension requires:

1. **CPU Request**: Select the number of vCPUs your extension needs from the dropdown menu.
2. **Memory Request**: Choose the amount of RAM your extension requires.

Note: The available memory options will change based on your CPU selection to ensure compatibility.

### Resource Pricing

As you select your resource configuration, you'll see an estimated cost per second and per hour. This helps you understand the running costs of your extension.

## Inputs

Define the inputs your extension will accept:

1. Click the "Add Input" button for each input you need.
2. For each input, provide:
   - **Name**: A descriptive name for the input.
   - **Key**: A unique identifier for the input (use snake_case, kebab-case, camelCase, or PascalCase).
   - **Description**: A brief explanation of what the input is for.
   - **Type**: Choose from String, Number, or Boolean.

## Outputs

Similarly, define the outputs your extension will produce:

1. Click the "Add Output" button for each output.
2. For each output, provide:
   - **Name**: A descriptive name for the output.
   - **Key**: A unique identifier for the output (follow the same naming conventions as inputs).
   - **Description**: A brief explanation of what the output represents.
   - **Type**: Choose from String, Number, or Boolean.

## Version Information (for updates)

If you're updating an existing extension:

1. **New Version**: Enter the version number for this update.
2. **Changelog**: Describe what's new or changed in this version.

## Finalizing Your Extension

1. Review all the information you've entered.
2. If creating a new extension, click "Create Extension".
3. If updating an existing extension, you can:
   - Click "Update Basic Info" to save changes to the extension details.
   - Click "Create New Version" to publish a new version with your configuration changes.

## Tips for Success

- Ensure your Docker image is properly configured and accessible.
- Be descriptive in your naming and descriptions to help users understand your extension.
- Consider the resource requirements carefully to balance performance and cost.
- Test your extension thoroughly before making it public.
- Keep your changelog informative for version updates.

By following these steps, you can create powerful, custom extensions that enhance the functionality of your workflows. Remember, you can always edit and update your extensions as needed.