# LLM-Agnostic Integration

## Contract-first approach

Business logic depends on the `LLMClient` protocol, not any vendor SDK.

Defined tools:

1. `search(query) -> list[SearchResult]`
2. `extract_offers(page_text, schema) -> dict`
3. `summarize_reviews(texts) -> dict`
4. `match_wine_entity(listed_name, candidates) -> dict`

## Providers

- `mock`: deterministic local provider for tests/dev.
- `generic_http`: adapter for any LLM gateway/API implementing JSON endpoints.

## Generic HTTP adapter configuration

Set:

- `LLM_PROVIDER=generic_http`
- `LLM_SEARCH_URL`
- `LLM_EXTRACT_OFFERS_URL`
- `LLM_SUMMARIZE_REVIEWS_URL`
- `LLM_MATCH_ENTITY_URL`
- `LLM_HEADERS_JSON` (optional auth headers)
- `LLM_TIMEOUT_SECONDS`

## Why this is provider agnostic

- No direct dependency on specific vendor package.
- Endpoint URLs are injected from config.
- Headers/auth are externalized.
- Pipeline calls only the protocol methods.

## Validation evidence

Unit tests verify:

- `mock` provider behavior,
- `generic_http` adapter request/response mapping,
- factory fallback and invalid config protection.
