# MySQL-ExecuteSelectQuery Extension

This extension executes a SELECT query on a MySQL database and retrieves the results.

## Requirements

- Python 3.11
- Redis
- MySQL database

## Installation

1. Build the Docker image:
   ```
   docker build -t mysql-execute-select-query .
   ```

2. Push the image to your container registry.

## Usage

Configure the extension in your workflow with the following inputs:

- `host`: MySQL server hostname
- `user`: MySQL username
- `password`: MySQL password
- `database`: Name of the database
- `query`: SELECT query to execute

Example workflow configuration:

```yaml
name: MySQL-ExecuteSelectQuery
description: Executes a SELECT query and retrieves results
extensionType: container
visibility: private
configuration:
  dockerImage: your-registry/mysql-execute-select-query
  dockerTag: latest
  inputs:
    - id: host
      name: MySQL Host
      description: MySQL server hostname
      type: string
      required: true
    - id: user
      name: MySQL User
      description: MySQL username
      type: string
      required: true
    - id: password
      name: MySQL Password
      description: MySQL password
      type: string
      required: true
    - id: database
      name: Database Name
      description: Name of the database
      type: string
      required: true
    - id: query
      name: SELECT Query
      description: SELECT query to execute
      type: string
      required: true
  outputs:
    - id: results
      name: Query Results
      description: Results of the executed query
      type: array
```

## Output

The extension returns a JSON object with the following structure:

```json
{
  "results": [
    {
      "column1": "value1",
      "column2": "value2",
      ...
    },
    ...
  ]
}
```

If an error occurs, the output will contain an "error" key with a description of the error.

## Error Handling

The extension handles various error scenarios, including:
- Missing input parameters
- Invalid JSON in input message
- Database connection errors
- Query execution errors

In case of an error, the extension will return an error message in the output.

## Security Considerations

- Ensure that the MySQL user has the minimum required permissions to execute the SELECT query.
- Use environment variables or secure secrets management for storing sensitive information like database credentials.
- Validate and sanitize the input query to prevent SQL injection attacks.

## Support

For issues and feature requests, please open an issue in the repository.