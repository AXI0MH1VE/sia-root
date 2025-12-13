from __future__ import annotations
from metacognition.graph_of_thoughts.planner import GraphOfThoughtsPlanner
from metacognition.visualization.graph_export import export_got_to_json

def supervisor_node(state):
    q = state["user_query"].lower()
    mode = "direct"
    if any(k in q for k in ["plan", "strategy", "roadmap", "wargame", "decision tree"]):
        mode = "plan"
    if any(k in q for k in ["who", "what", "when", "contract", "clause", "email", "document", "history"]):
        mode = "retrieve"
    state["mode"] = mode
    state.setdefault("trace", {})["supervisor_mode"] = mode
    return state

def plan_node(state):
    planner = GraphOfThoughtsPlanner()
    res = planner.plan(state["user_query"], depth=2, width=3)
    state["plan"] = res.final.content
    state.setdefault("trace", {})["got_graph"] = export_got_to_json(res.explored)
    return state
