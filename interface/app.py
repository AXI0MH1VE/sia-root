from __future__ import annotations
import os
import hashlib
import numpy as np
import streamlit as st
from dotenv import load_dotenv

from l0_alignment.policy import L0Policy
from core_inference.context_manager import ContextManager

from orchestration.state_graph import build_graph
from orchestration.supervisor_agent import supervisor_node, plan_node
from orchestration.retrieval import retrieve_node
from orchestration.respond import respond_node

from memory_store.memgpt_lite.memory_kernel import LanceMemory
from memory_store.graph_rag.entity_extractor import extract_triplets
from memory_store.graph_rag.neo4j_connector import Neo4jConnector, Neo4jConfig

load_dotenv()

st.set_page_config(page_title="SIA", layout="wide")
st.title("SIA — Strategic Insider Assistant")

if "ctx" not in st.session_state:
    st.session_state.ctx = ContextManager(max_turns=18)

policy = L0Policy()

with st.sidebar:
    st.header("Runtime")
    st.write(f"Security mode: `{os.getenv('SIA_SECURITY_MODE','standard')}`")
    st.write(f"llama.cpp endpoint: `{os.getenv('LLAMA_CPP_URL','')}`")
    show_trace = st.toggle("Show trace", value=True)
    show_graph = st.toggle("Show GoT graph JSON", value=False)

st.subheader("Chat")
user_in = st.text_area("Your query", height=120)

col1, col2 = st.columns([1, 1])
run_btn = col1.button("Run SIA", type="primary")
ingest_btn = col2.button("Ingest note to memory")

def ingest_note(text: str) -> str:
    data_dir = os.getenv("SIA_DATA_DIR", "./data")
    lancedb_path = os.getenv("LANCEDB_PATH", os.path.join(data_dir, "lancedb"))
    mem = LanceMemory(lancedb_path)

    h = hashlib.sha256(text.encode("utf-8")).digest()
    rng = np.random.default_rng(int.from_bytes(h[:8], "little"))
    emb = rng.standard_normal(384).astype("float32")
    emb /= max(float(np.linalg.norm(emb)), 1e-6)

    doc_id = f"doc_{int.from_bytes(h[:6],'little')}"
    mem.upsert(doc_id=doc_id, text=text, embedding=emb, meta={"source":"manual_ingest"})

    cfg = Neo4jConfig(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "please_change_me"),
    )
    try:
        conn = Neo4jConnector(cfg)
        conn.ensure_schema()
        trips = extract_triplets(text)
        formatted = [(f"ent_{abs(hash(t.subject))%(10**12)}", t.subject, t.predicate, t.obj) for t in trips]
        conn.upsert_triplets(formatted)
        conn.close()
        return f"Ingested {doc_id} (vector) + {len(trips)} triplets (graph)."
    except Exception as e:
        return f"Ingested {doc_id} (vector). Graph ingest failed: {e}"

def run_sia(query: str):
    d = policy.check_input(query)
    if not d.allowed:
        return {"response": f"REJECTED by L0 Temple: {d.reason}", "trace": {"l0": d.reason}}

    st.session_state.ctx.add("user", d.sanitized)

    graph = build_graph(
        supervisor_node=supervisor_node,
        retrieve_node=retrieve_node,
        plan_node=plan_node,
        respond_node=respond_node,
    )
    out = graph.invoke({"user_query": d.sanitized, "trace": {}})

    out_dec = policy.check_output(out.get("response", ""))
    if not out_dec.allowed:
        out["response"] = f"REJECTED by L0 Temple (output): {out_dec.reason}"

    st.session_state.ctx.add("assistant", out["response"])
    return out

if ingest_btn and user_in.strip():
    st.success(ingest_note(user_in.strip()))

if run_btn and user_in.strip():
    out = run_sia(user_in.strip())
    st.markdown("### Response")
    st.write(out.get("response", ""))

    if show_trace:
        st.markdown("### Trace")
        st.json(out.get("trace", {}))

    if show_graph:
        got = out.get("trace", {}).get("got_graph")
        if got:
            st.markdown("### GoT Graph JSON")
            st.json(got)

st.markdown("---")
st.subheader("Conversation")
for role, content in st.session_state.ctx.turns:
    st.markdown(f"**{role.upper()}**: {content}")
