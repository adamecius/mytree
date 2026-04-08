import networkx as nx


def neighbors(graph: nx.Graph, node: str) -> list[str]:
    if node not in graph:
        return []
    return sorted(graph.neighbors(node))
