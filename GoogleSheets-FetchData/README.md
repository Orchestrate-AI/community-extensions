# Google Sheets - Fetch Data Extension

This extension retrieves data from a specified range in a Google Sheets spreadsheet.

## Requirements

- Google Cloud project with Google Sheets API enabled
- Service account credentials with access to the target spreadsheet

## Configuration

```yaml
name: Google Sheets - Fetch Data
description: Retrieves data from a specified range in a Google Sheets spreadsheet
extensionType: container
visibility: private
configuration:
  dockerImage: ghcr.io/orchestrate-ai/google-sheets-fetch-data
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: spreadsheet_id
      name: Spreadsheet ID
      description: The ID of the Google Sheets spreadsheet
      key: spreadsheet_id
      type: string
      required: true
    - id: range_name
      name: Range Name
      description: The A1 notation of the range to retrieve
      key: range_name
      type: string
      required: true
    - id: credentials_json
      name: Service Account Credentials
      description: JSON string of the service account credentials
      key: credentials_json
      type: string
      required: true
  outputs:
    - id: data
      name: Fetched Data
      description: The data retrieved from the specified range
      key: data
      type: array
```

## Usage

1. Ensure you have a Google Cloud project with the Google Sheets API enabled.
2. Create a service account and download the JSON key file.
3. Share the target Google Sheets spreadsheet with the service account email.
4. Use the extension in your workflow, providing the required inputs:
   - `spreadsheet_id`: The ID of the spreadsheet (found in the URL)
   - `range_name`: The A1 notation of the range to retrieve (e.g., "Sheet1!A1:C10")
   - `credentials_json`: The contents of the service account JSON key file as a string

The extension will return the fetched data as an array of arrays, where each inner array represents a row from the specified range.