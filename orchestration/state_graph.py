from __future__ import annotations
from typing import TypedDict, Any
from langgraph.graph import StateGraph, END

class SIAState(TypedDict, total=False):
    user_query: str
    mode: str
    retrieved: dict
    plan: str
    response: str
    trace: dict[str, Any]

def build_graph(supervisor_node, retrieve_node, plan_node, respond_node):
    g = StateGraph(SIAState)
    g.add_node("supervisor", supervisor_node)
    g.add_node("retrieve", retrieve_node)
    g.add_node("plan", plan_node)
    g.add_node("respond", respond_node)
    g.set_entry_point("supervisor")

    def route(state: SIAState):
        m = state.get("mode", "direct")
        if m == "retrieve":
            return "retrieve"
        if m == "plan":
            return "plan"
        return "respond"

    g.add_conditional_edges("supervisor", route, {"retrieve": "retrieve", "plan": "plan", "respond": "respond"})
    g.add_edge("retrieve", "respond")
    g.add_edge("plan", "respond")
    g.add_edge("respond", END)
    return g.compile()
