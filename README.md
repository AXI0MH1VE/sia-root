# Strategic Insider Assistant (SIA)

SIA is a **sovereign**, **modular**, **hierarchical** intelligence system organized as:
- **L0 Temple**: alignment + drift/poisoning defenses
- **Core Inference**: local inference via `llama.cpp` server (drop-in for Mamba/Jamba GGUF or other local models)
- **Metacognition Temple**: Graph-of-Thoughts planner + optional causal inference
- **Memory Store**: GraphRAG (Neo4j) + vector store (LanceDB)
- **Orchestration**: LangGraph state machine
- **Interface**: Streamlit

Model weights are intentionally **not** included. Inference is real and runs against your **locally hosted** runtime.

## Quickstart

### 1) Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2) Start Neo4j
```bash
docker compose up -d
```

### 3) Start a local `llama.cpp` server
Example (adjust path/flags):
```bash
./server -m /path/to/model.gguf -c 8192 --host 127.0.0.1 --port 8080
```

### 4) Run the UI
```bash
streamlit run interface/app.py
```

## Notes
- L0 policy is deterministic and fails closed.
- Drift detection utilities (PSI/KL) are included for embedding distribution monitoring.
- GraphRAG ingest works offline (regex triplet extraction) and inserts into Neo4j.
- Vector memory uses LanceDB with a deterministic local embedding fallback.
