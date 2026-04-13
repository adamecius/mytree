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

## Document OCR to Markdown Utility

This repository includes a dedicated utility package at `utility/image_reader` that converts image-based PDF or DjVu files to Markdown using a DeepSeek vision model, with progress, elapsed time, ETA, and multi-GPU dispatch.

### Requirements plan

1. **System packages** (required for page rasterization):
   - PDF support: `pdftoppm` from `poppler-utils`
   - DjVu support: `djvused` and `ddjvu` from `djvulibre-bin`
2. **Python runtime**:
   - Python `>=3.11`
3. **Python dependencies**:
   - Installed from this project (`pip install -e .`) including `openai` dependency
4. **DeepSeek API configuration**:
   - `DEEPSEEK_API_KEY` must be set (or pass `--api-key`)
   - Optional: `DEEPSEEK_BASE_URL` for compatible endpoints
5. **GPU setup (optional but recommended)**:
   - CUDA-enabled environment when using multi-GPU mode (`--gpus 0,1,...`)

### Installation instructions (pip + all requirements)

#### Ubuntu / Debian

```bash
sudo apt-get update
sudo apt-get install -y poppler-utils djvulibre-bin python3-venv

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

#### macOS (Homebrew)

```bash
brew install poppler djvulibre python@3.11

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

### Usage

```bash
export DEEPSEEK_API_KEY="<your_key>"
doc2md-deepseek ./input.pdf ./output.md \
  --model deepseek-vl2 \
  --gpus 0,1
```

### Useful flags

- `--api-key`: pass API key directly (instead of env var)
- `--base-url`: override API URL for DeepSeek-compatible endpoints
- `--gpus`: comma-separated GPU IDs (example: `0,1,2,3`)
- `--dpi`: page extraction quality (default: `300`)
- `--json-summary`: emit machine-readable completion summary
