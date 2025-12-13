from __future__ import annotations
from .node import ThoughtNode
from typing import Sequence

def generator(seed: ThoughtNode, prompts: Sequence[str]) -> list[ThoughtNode]:
    return [ThoughtNode(content=p.format(seed=seed.content), parent_id=seed.node_id) for p in prompts]

def aggregator(best: Sequence[ThoughtNode]) -> ThoughtNode:
    merged = "\n\n".join([f"- ({n.score:.2f}) {n.content}" for n in best])
    return ThoughtNode(content=f"SYNTHESIS:\n{merged}", parent_id=best[0].parent_id if best else None)
