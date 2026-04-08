# API module

## Why this module exists
This folder contains the HTTP interface for the assistant service. It isolates transport/API concerns from graph, retrieval, and optimization logic.

## Files
- `app.py`: FastAPI application bootstrap and router registration.
- `routes/`: endpoint handlers grouped by concern (`health`, `query`, `metrics`).
- `schemas/`: request/response data models.

## Function one-liners
- `app` (in `app.py`): creates and wires the API service instance.
