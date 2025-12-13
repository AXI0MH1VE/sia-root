from __future__ import annotations

def prune_low_score(graph_json: dict, min_score: float = 0.5) -> dict:
    nodes = graph_json.get("nodes", [])
    keep = [n for n in nodes if n.get("score", 0.0) >= min_score or n.get("parent") is None]
    keep_ids = {n["id"] for n in keep}
    for n in keep:
        if n.get("parent") and n["parent"] not in keep_ids:
            n["parent"] = None
    return {"nodes": keep}
