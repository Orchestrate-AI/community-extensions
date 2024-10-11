# ZillowScraper-ScrapeListings Extension

This extension scrapes Zillow listings based on a given price range and zipcode.

## Description

The ZillowScraper-ScrapeListings extension allows you to fetch real estate listings from Zillow for a specific zipcode within a defined price range. It uses web scraping techniques to gather information about available properties, including their addresses, prices, and other details.

## Requirements

- Docker
- Access to a Redis instance

## Usage

This extension is designed to be used as part of a workflow system. It communicates via Redis channels and expects input in a specific format.

### Input Format

The extension expects a JSON input with the following structure:

```json
{
  "inputs": {
    "zipcode": "12345",
    "min_price": 100000,
    "max_price": 500000
  }
}
```

### Output Format

The extension returns a JSON output with the following structure:

```json
{
  "listings": [
    {
      "address": "123 Main St, City, State 12345",
      "price": "$300,000",
      "details": "3 bds | 2 ba | 1,500 sqft",
      "link": "https://www.zillow.com/homedetails/..."
    },
    ...
  ],
  "count": 10
}
```

## Building and Deployment

1. Build the Docker image:
   ```
   docker build -t zillow-scraper-extension .
   ```

2. Push the image to your container registry:
   ```
   docker tag zillow-scraper-extension your-registry/zillow-scraper-extension:latest
   docker push your-registry/zillow-scraper-extension:latest
   ```

3. Use the following YAML configuration in your workflow system:

```yaml
name: ZillowScraper-ScrapeListings
description: Scrape Zillow listings based on price range and zipcode
extensionType: container
visibility: private
configuration:
  dockerImage: your-registry/zillow-scraper-extension
  dockerTag: latest
  cpuRequest: "0.1"
  memoryRequest: "128Mi"
  inputs:
    - id: zipcode
      name: Zipcode
      description: The zipcode to search for listings
      key: zipcode
      type: string
      required: true
    - id: min_price
      name: Minimum Price
      description: The minimum price for listings
      key: min_price
      type: number
      required: true
    - id: max_price
      name: Maximum Price
      description: The maximum price for listings
      key: max_price
      type: number
      required: true
  outputs:
    - id: listings
      name: Listings
      description: The scraped Zillow listings
      key: listings
      type: array
    - id: count
      name: Count
      description: The number of listings found
      key: count
      type: number
```

## Notes

- This extension uses web scraping, which may be against Zillow's terms of service. Ensure you have the right to use this extension and consider rate limiting to avoid overloading Zillow's servers.
- The extension requires the following environment variables to be set:
  - WORKFLOW_INSTANCE_ID
  - WORKFLOW_EXTENSION_ID
  - REDIS_HOST_URL
  - REDIS_USERNAME
  - REDIS_PASSWORD
  - REDIS_CHANNEL_IN
  - REDIS_CHANNEL_OUT
  - REDIS_CHANNEL_READY

## Support

For issues or questions, please open an issue in the repository where this extension is hosted.