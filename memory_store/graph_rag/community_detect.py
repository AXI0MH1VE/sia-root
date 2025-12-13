from __future__ import annotations
import networkx as nx

def build_graph_from_triplets(triplets: list[dict]) -> nx.DiGraph:
    g = nx.DiGraph()
    for t in triplets:
        s = t.get("subject") or ""
        p = t.get("predicate") or ""
        o = t.get("object") or ""
        if s and o:
            g.add_edge(s, o, predicate=p)
    return g

def louvain_communities_undirected(g: nx.Graph):
    from networkx.algorithms.community import louvain_communities
    return louvain_communities(g, seed=42)
