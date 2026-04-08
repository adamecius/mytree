import importlib.util

import pytest

from mcp.server import list_tools
from mcp.tools.retrieve_tool import retrieve

NETWORKX_INSTALLED = importlib.util.find_spec("networkx") is not None

if NETWORKX_INSTALLED:
    import networkx as nx

    from mcp.tools.graph_tool import neighbors


def test_list_tools_is_sorted() -> None:
    assert list_tools() == ["graph_neighbors", "retrieve"]


def test_retrieve_respects_k() -> None:
    result = retrieve("hello", k=3)
    assert len(result) == 3
    assert result[0].startswith("retrieved_chunk_1")


@pytest.mark.skipif(not NETWORKX_INSTALLED, reason="networkx is not installed")
def test_neighbors_for_missing_node() -> None:
    graph = nx.Graph()
    graph.add_edge("a", "b")
    assert neighbors(graph, "unknown") == []
