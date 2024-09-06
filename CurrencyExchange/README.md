# Currency Exchange Extension

This extension provides the most recent currency exchange rates for a given base currency and a list of target currencies. It uses the Open Exchange Rates API to fetch the latest exchange rates.

## Inputs

The extension accepts the following inputs:

1. `app_id` (required):
   - Type: string
   - Description: Your App ID for the Open Exchange Rates API
   - How to obtain: Sign up at [https://openexchangerates.org/signup](https://openexchangerates.org/signup) to get your free App ID

2. `base_currency` (optional):
   - Type: string
   - Description: The base currency code (e.g., "USD", "EUR", "GBP")
   - Default: "USD"
   - Note: The free tier only supports USD as the base currency. For other base currencies, you'll need a paid plan.

3. `target_currencies` (required):
   - Type: string
   - Description: A comma-separated list of target currency codes
   - Example: "EUR,GBP,JPY,CAD"

## Outputs

The extension provides the following outputs:

1. `base_currency`:
   - Type: string
   - Description: The base currency code used for the exchange rates

2. `date`:
   - Type: number
   - Description: The timestamp of the exchange rate data (Unix timestamp)

3. `rates`:
   - Type: object
   - Description: An object containing the exchange rates for the requested target currencies
   - Example:
     ```json
     {
       "EUR": 0.84,
       "GBP": 0.72,
       "JPY": 110.25,
       "CAD": 1.25
     }
     ```

## Usage Example

Here's an example of how to use the Currency Exchange Extension:
