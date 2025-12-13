from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()

from l0_alignment.policy import L0Policy
from orchestration.state_graph import build_graph
from orchestration.supervisor_agent import supervisor_node, plan_node
from orchestration.retrieval import retrieve_node
from orchestration.respond import respond_node

def main():
    policy = L0Policy()
    q = input("SIA> ").strip()
    d = policy.check_input(q)
    if not d.allowed:
        print(f"REJECTED: {d.reason}")
        return
    graph = build_graph(supervisor_node, retrieve_node, plan_node, respond_node)
    out = graph.invoke({"user_query": d.sanitized, "trace": {}})
    print(out.get("response", ""))

if __name__ == "__main__":
    main()
