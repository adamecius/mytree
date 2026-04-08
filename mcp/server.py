"""MCP server scaffold.

Replace placeholders with the selected Python MCP SDK implementation.
"""

TOOL_REGISTRY = {
    "retrieve": "Hybrid KG/vector retrieval",
    "graph_neighbors": "Graph neighborhood lookup",
}


def list_tools() -> list[str]:
    return sorted(TOOL_REGISTRY.keys())
