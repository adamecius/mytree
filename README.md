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

## Available API Endpoints

- `GET /health`
- `POST /query`
- `POST /batch_query`
- `GET /metrics`

## Materials Ontology Graph

The graph is implemented as a typed `networkx.MultiDiGraph` with three layers:

- `physics`
- `math`
- `numerics`

Builder and utilities are under `kg/graph_build/materials_ontology.py`, including:

- `build_materials_ontology_graph()`
- `validate_graph_structure(graph)`
- `node_neighborhood_subgraph(graph, node_id)`

### Visualization toolset

- Draw full graph:

```bash
python -m kg.graph_build.cli --draw-all artifacts/materials_graph.png
```

- Draw single-node neighborhood:

```bash
python -m kg.graph_build.cli \
  --node-id phys:born_oppenheimer \
  --draw-node artifacts/born_oppenheimer_neighbors.png
```

- Validate ontology rules:

```bash
python -m kg.graph_build.cli --validate
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn api.app:app --reload
```
