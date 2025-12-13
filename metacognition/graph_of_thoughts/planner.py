from __future__ import annotations
from dataclasses import dataclass
from .node import ThoughtNode
from .transformations import generator, aggregator
from .scoring import HeuristicScorer

@dataclass
class GoTPlanResult:
    final: ThoughtNode
    explored: list[ThoughtNode]

class GraphOfThoughtsPlanner:
    def __init__(self, scorer=None):
        self.scorer = scorer or HeuristicScorer()

    def plan(self, objective: str, depth: int = 2, width: int = 3) -> GoTPlanResult:
        root = ThoughtNode(content=objective, parent_id=None)
        explored = [root]
        frontier = [root]

        prompts = [
            "Strategy A: Decompose objective '{seed}' into 3 milestones with risks + mitigations.",
            "Strategy B: Identify leverage points + constraints for '{seed}', propose a 2-week plan.",
            "Strategy C: Assume budget limits. Propose a minimal viable path for '{seed}' with guardrails.",
            "Strategy D: Red-team failure modes for '{seed}' and propose prevention controls.",
        ]

        for _ in range(depth):
            next_frontier: list[ThoughtNode] = []
            for node in frontier:
                children = generator(node, prompts[:width])
                for c in children:
                    c.score = self.scorer.score(c.content)
                explored.extend(children)
                next_frontier.extend(sorted(children, key=lambda n: n.score, reverse=True)[:width])
            frontier = next_frontier

        leaves = sorted(frontier, key=lambda n: n.score, reverse=True)[:max(1, width)]
        final = aggregator(leaves)
        final.score = self.scorer.score(final.content)
        explored.append(final)
        return GoTPlanResult(final=final, explored=explored)
