from __future__ import annotations
from typing import Any
from metacognition.graph_of_thoughts.node import ThoughtNode

def export_got_to_json(nodes: list[ThoughtNode]) -> dict[str, Any]:
    return {
        "nodes": [
            {
                "id": n.node_id,
                "parent": n.parent_id,
                "label": (n.content[:80] + ("..." if len(n.content) > 80 else "")),
                "score": n.score,
                "content": n.content,
            }
            for n in nodes
        ]
    }
