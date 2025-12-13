from __future__ import annotations
import os
import numpy as np
import hashlib
from memory_store.memgpt_lite.memory_kernel import LanceMemory
from memory_store.graph_rag.neo4j_connector import Neo4jConnector, Neo4jConfig

def embed_deterministic(text: str, dim: int = 384) -> np.ndarray:
    h = hashlib.sha256(text.encode("utf-8")).digest()
    rng = np.random.default_rng(int.from_bytes(h[:8], "little"))
    v = rng.standard_normal(dim).astype(np.float32)
    v /= max(float(np.linalg.norm(v)), 1e-6)
    return v

def retrieve_node(state):
    data_dir = os.getenv("SIA_DATA_DIR", "./data")
    lancedb_path = os.getenv("LANCEDB_PATH", os.path.join(data_dir, "lancedb"))
    mem = LanceMemory(lancedb_path)

    q = state["user_query"]
    q_emb = embed_deterministic(q)
    hits = mem.search(q_emb, k=5)

    cfg = Neo4jConfig(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "please_change_me"),
    )
    graph_hits = []
    try:
        conn = Neo4jConnector(cfg)
        conn.ensure_schema()
        graph_hits = conn.neighborhood(q, limit=20)
        conn.close()
    except Exception as e:
        graph_hits = [{"error": str(e)}]

    state["retrieved"] = {
        "vector_hits": [{"text": h.text, "score": h.score, "meta": h.meta} for h in hits],
        "graph_hits": graph_hits,
    }
    state.setdefault("trace", {})["retrieval_counts"] = {"vector": len(hits), "graph": len(graph_hits)}
    return state
