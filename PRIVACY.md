# Privacy Policy

This plugin connects Dify to the DataForB2B API (`https://api.dataforb2b.ai`).

## Data collected and processed

- **API key**: Stored by Dify as an encrypted credential and sent in the `api_key` header of each request to authenticate with DataForB2B. It is never logged by the plugin.
- **Tool inputs**: The query, filters, and profile/company identifiers you provide are sent to the DataForB2B API solely to perform the requested search or enrichment.
- **Tool outputs**: B2B profile and company data returned by the API (which may include professional contact details such as work emails or phone numbers when explicitly requested) is passed back into your Dify app. The plugin does not store, cache, or transmit this data anywhere else.

## Third-party services

Requests are sent to DataForB2B, which processes them under its own terms and privacy policy:

- Terms & Privacy: https://dataforb2b.ai
- Documentation: https://docs.dataforb2b.ai

## Data retention

This plugin does not persist any data. It performs stateless API calls and returns the results to your Dify workflow. Any retention of inputs or results is governed by your Dify instance and by DataForB2B.

## Contact

For privacy questions, contact contact@dataforb2b.ai.
