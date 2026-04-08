# Architecture Overview

## Components

1. **KG Pipeline (`kg/`)**: Ingests data, extracts entities/relations, and builds graph artifacts.
2. **RAG Pipeline (`rag/`)**: Produces chunks, retrieves context via graph + vector methods, and assembles prompt context.
3. **Assistant API (`api/`)**: Exposes `/query`, `/batch_query` (future), `/health`, and `/metrics` (future).
4. **MCP Layer (`mcp/`)**: Wraps retrieval and graph operations as tools for assistant orchestration.
5. **Optimizer (`optimizer/`)**: Runs offline metaheuristics over retrieval/graph configuration.
6. **Benchmark (`benchmark/`)**: Evaluates retrieval and answer quality with reproducible experiments.

## Initial Milestones

- Baseline KG build and retrieval quality report.
- End-to-end `/query` path using retrieval placeholder.
- Offline optimization runner with one objective and one metaheuristic.
- Benchmark report comparing baseline vs optimized settings.
