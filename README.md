# DataForB2B

Power your sales or recruiting AI agent with live B2B data. DataForB2B is a people and company search API with 70+ filters including job title, skills, company size, LinkedIn URL, funding stage, investor, past employers, certifications, years of experience, GitHub repositories, languages and more.

Use it directly from Dify to build prospecting agents and lead-enrichment workflows, powered by the [DataForB2B](https://dataforb2b.ai) API.

## Tools

| Tool | What it does |
|------|--------------|
| **Search People** | Search professional profiles. Build conditions with filter slots (column + operator + value), combined with AND or OR. |
| **Search Companies** | Search companies by industry, size, location, funding, growth and more, using the same filter slots. |
| **Enrich Profile** | Enrich a person from a profile URL or id — full profile, professional/personal email, phone, and GitHub. You only pay for the data you request. |
| **Enrich Company** | Enrich a company from its name, domain, URL or id — size, locations, funding rounds, investors and growth. |
| **Reasoning Search** | Describe who you want in plain language; an AI agent builds and runs the optimal search, asking clarifying questions when needed. |
| **Typeahead** | Autocomplete the exact stored value for any filter (company, industry, title, skill, school, investor, location...) so your search matches the database. |

## Setup

1. Install the **DataForB2B** plugin from the Dify Marketplace.
2. Sign up at [app.dataforb2b.ai](https://app.dataforb2b.ai) and generate an API key under **Settings > API Keys**.
3. Open the plugin's **Authorize** dialog and paste your API key.
4. Add any DataForB2B tool to an Agent or Workflow and run it.

## Filters

`Search People` and `Search Companies` use **filter slots**: each slot is a **column** (dropdown), an **operator** (dropdown) and a **value**. Up to 5 slots are combined with the **Match logic** (AND / OR).

- Operators: `=`, `like` (contains), `in`, `>`, `>=`, `<`, `<=`, `between`.
- For `in`, give a comma-separated value, e.g. `US, GB, FR`.
- For `between`, give `min,max`, e.g. `5,10`.
- For nested / mixed logic, use the **Advanced filters (JSON)** field, which is combined (AND) with the slots:

```json
{ "op": "or", "conditions": [
  { "column": "skill", "type": "=", "value": "Python" },
  { "column": "skill", "type": "=", "value": "Go" }
] }
```

Tip: use the **Typeahead** tool to resolve the exact stored value for a column before filtering. See the [API reference](https://docs.dataforb2b.ai) for the full list of columns.

## Credits

Calls consume credits from your DataForB2B account. Search and enrichment default to cached data (`enrich_live: false`, lower cost); enable live enrichment for fresh data at a higher rate. Enrich Profile bills only for the data types you enable.

## Links

- Website: https://dataforb2b.ai
- Documentation: https://docs.dataforb2b.ai
- Source code: https://github.com/DataForB2B/dataforb2b-dify-plugin
- Support: contact@dataforb2b.ai
