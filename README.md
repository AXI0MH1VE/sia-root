# Strategic Insider Assistant (SIA)

The **Strategic Insider Assistant (SIA)** is a cutting-edge, **sovereign**, **modular**, and **hierarchical** intelligence system designed for advanced reasoning, memory management, and aligned inference. It is built on a robust, multi-component architecture that ensures safety, context-awareness, and complex planning capabilities.

SIA is designed to run against your **locally hosted** runtime, ensuring data privacy and control. **Model weights are intentionally not included** in this repository.

## Architecture Overview

The system is organized into distinct, modular temples, each responsible for a core function:

| Component | Purpose | Key Technology |
| :--- | :--- | :--- |
| **L0 Temple** | Alignment and Safety | Policy-based alignment, Drift/Poisoning Defenses |
| **Core Inference** | Local Model Execution | `llama.cpp` server (Drop-in for Mamba/Jamba GGUF or other local models) |
| **Metacognition Temple** | Advanced Planning & Reasoning | Graph-of-Thoughts (GoT) Planner, Optional Causal Inference |
| **Memory Store** | Knowledge Management | GraphRAG (Neo4j), Vector Store (LanceDB) |
| **Orchestration** | System Control Flow | LangGraph State Machine |
| **Interface** | User Interaction | Streamlit Web Application |

### Technical Details

*   **L0 Policy:** The L0 alignment policy is deterministic and designed to "fail closed" for maximum safety.
*   **Drift Detection:** Utilities for Population Stability Index (PSI) and Kullback-Leibler (KL) divergence are included for monitoring embedding distribution stability.
*   **GraphRAG:** Knowledge graph ingestion works offline using regex triplet extraction before inserting data into the Neo4j database.
*   **Vector Memory:** Utilizes LanceDB with a deterministic local embedding fallback for reliable vector storage.

## Quickstart

Follow these steps to set up and run the SIA system locally.

### 1. Installation

Set up the Python environment and install dependencies.

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install required Python packages
pip install -r requirements.txt

# Copy the example environment file
cp .env.example .env
```

### 2. Start Neo4j Database

The Memory Store requires a running Neo4j instance. Use the provided Docker Compose file to start the database.

```bash
docker compose up -d
```

### 3. Start Local LLM Server

SIA requires a local `llama.cpp` server to handle inference. You must provide your own GGUF model weights.

```bash
# Example command (adjust path/flags for your model)
./server -m /path/to/model.gguf -c 8192 --host 127.0.0.1 --port 8080
```

### 4. Run the User Interface

Once the dependencies are running, start the Streamlit application.

```bash
streamlit run interface/app.py
```
