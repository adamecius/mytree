# KG Assistant

Python repository scaffold for an AI Assistant API with MCP-style tools, KG-RAG retrieval, offline metaheuristic optimization, and benchmarking.

## Project Layout

- `api/`: FastAPI application and routes.
- `mcp/`: MCP server entrypoint and tool implementations.
- `kg/`: Knowledge graph ingestion, extraction, build, and storage modules.
- `rag/`: Chunking, retrieval, reranking, and context assembly.
- `optimizer/`: Offline objective functions and metaheuristic runners.
- `benchmark/`: Datasets, evaluators, metrics, and reports.
- `experiments/`: Experiment configs and outputs.
- `tests/`: Test suite.
- `docs/`: Architecture and operational docs.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn api.app:app --reload
```

## Next Steps

1. Implement data ingestion and graph construction in `kg/`.
2. Implement hybrid retrieval in `rag/`.
3. Wire retrieval and graph tools into `mcp/server.py`.
4. Add benchmark fixtures and baseline evaluation in `benchmark/`.
5. Add optimizer search loops in `optimizer/`.
