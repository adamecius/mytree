# API routes

## Why this module exists
This folder separates endpoint handlers by responsibility so each route file stays small and maintainable.

## Files
- `health.py`: liveness endpoint for service checks.
- `query.py`: single and batch query handlers.
- `metrics.py`: lightweight service metadata endpoint.

## Function one-liners
- `health()`: returns service liveness payload.
- `query()`: answers one user query using retrieval placeholders.
- `batch_query()`: answers multiple questions in one call.
- `metrics()`: returns service/version/tool metadata.
