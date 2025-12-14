from __future__ import annotations
from typing import Any, Dict, List
from .node import ThoughtNode
from .scoring import HeuristicScorer
from .transformations import generator, aggregator
from core_inference.model_loader import LLM_CLIENT

class GoTPlanner:
    """
    A simplified Graph-of-Thoughts (GoT) Planner that uses a fixed, two-step
    thought process: Generate multiple initial thoughts, then aggregate the best ones.
    It integrates with the LLM_CLIENT for thought generation.
    """
    def __init__(self, scorer: HeuristicScorer | None = None):
        self.scorer = scorer or HeuristicScorer()
        self.graph: Dict[str, ThoughtNode] = {}
        self.trace: Dict[str, Any] = {}

    def _generate_thoughts(self, seed_node: ThoughtNode, num_thoughts: int = 3) -> List[ThoughtNode]:
        """
        Uses the LLM to generate multiple distinct thoughts based on the seed.
        """
        prompts = [
            f"Critically analyze the following statement and propose a counter-argument: {seed_node.content}",
            f"Expand on the implications of the following statement, focusing on risk: {seed_node.content}",
            f"Propose a concrete action plan based on the following statement: {seed_node.content}",
        ]
        
        generated_contents = []
        for prompt in prompts[:num_thoughts]:
            # Use the LLM client to generate the thought content
            content = LLM_CLIENT.get_completion(
                prompt=f"You are a strategic planner. {prompt}",
                max_tokens=256,
                temperature=0.8
            )
            generated_contents.append(content)

        # Create ThoughtNodes from the generated content
        new_nodes = [
            ThoughtNode(content=c, parent_id=seed_node.node_id)
            for c in generated_contents
        ]
        
        return new_nodes

    def _score_and_select(self, nodes: List[ThoughtNode], k: int = 1) -> List[ThoughtNode]:
        """Scores all nodes and selects the top k."""
        for node in nodes:
            node.score = self.scorer.score(node.content)
        
        # Sort by score in descending order
        sorted_nodes = sorted(nodes, key=lambda n: n.score, reverse=True)
        return sorted_nodes[:k]

    def plan(self, initial_query: str) -> str:
        """
        Executes the simplified GoT planning process.
        """
        self.graph = {}
        self.trace = {"steps": []}
        
        # 1. Initial Seed Node
        seed_node = ThoughtNode(content=initial_query, parent_id=None)
        self.graph[seed_node.node_id] = seed_node
        self.trace["steps"].append({"step": "Seed", "content": seed_node.content})

        # 2. Generation Step
        generated_nodes = self._generate_thoughts(seed_node, num_thoughts=3)
        for node in generated_nodes:
            self.graph[node.node_id] = node
        self.trace["steps"].append({"step": "Generate", "count": len(generated_nodes)})

        # 3. Scoring and Selection
        best_nodes = self._score_and_select(generated_nodes, k=2)
        self.trace["steps"].append({"step": "Score & Select", "best_scores": [n.score for n in best_nodes]})

        # 4. Aggregation Step
        final_thought = aggregator(best_nodes)
        self.graph[final_thought.node_id] = final_thought
        self.trace["steps"].append({"step": "Aggregate", "content": final_thought.content})

        # 5. Final LLM Synthesis (Optional, but good for a clean output)
        synthesis_prompt = f"Based on the following aggregated strategic thought, provide a final, concise action recommendation:\n\n{final_thought.content}"
        final_recommendation = LLM_CLIENT.get_completion(
            prompt=synthesis_prompt,
            max_tokens=128,
            temperature=0.5
        )
        
        self.trace["final_recommendation"] = final_recommendation
        
        return final_recommendation

    def get_trace(self) -> Dict[str, Any]:
        """Returns the execution trace for visualization/debugging."""
        # For a full trace, we can include the graph structure
        graph_export = {
            "nodes": [{"id": n.node_id, "content": n.content, "score": n.score, "parent": n.parent_id} for n in self.graph.values()],
            "edges": [{"source": n.parent_id, "target": n.node_id} for n in self.graph.values() if n.parent_id]
        }
        self.trace["got_graph"] = graph_export
        return self.trace
