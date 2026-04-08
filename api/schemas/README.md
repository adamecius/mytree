# API schemas

## Why this module exists
This folder centralizes typed contracts for input/output payloads to keep validation and docs consistent.

## Files
- `query.py`: Pydantic models for query, batch query, and metrics responses.

## Function one-liners
- `QueryRequest`: schema for single-question requests.
- `QueryResponse`: schema for single-question answers.
- `BatchQueryRequest`: schema for batch-question requests.
- `BatchQueryResponse`: schema for batch answers.
- `MetricsResponse`: schema for service metadata responses.
