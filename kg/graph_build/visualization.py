from __future__ import annotations

from pathlib import Path

import networkx as nx

from kg.graph_build.materials_ontology import layered_positions, node_neighborhood_subgraph


def _relation_color(relation: str) -> str:
    return {
        "approximation_of": "#2d6cdf",
        "represented_by": "#15a37d",
        "solved_by": "#cc7a00",
    }.get(relation, "#666666")


def _layer_color(layer: str) -> str:
    return {
        "physics": "#7a1f8a",
        "math": "#1f5f8a",
        "numerics": "#8a5f1f",
    }.get(layer, "#555555")


def draw_graph(graph: nx.MultiDiGraph, output_path: str | Path, title: str = "Materials Ontology") -> Path:
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("matplotlib is required for visualization") from exc

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    pos = layered_positions(graph)
    fig, ax = plt.subplots(figsize=(16, 8))

    node_colors = [_layer_color(data.get("layer", "")) for _, data in graph.nodes(data=True)]
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=1400, alpha=0.9, ax=ax)

    node_labels = {n: d.get("label", n) for n, d in graph.nodes(data=True)}
    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=8, ax=ax)

    for relation in ("approximation_of", "represented_by", "solved_by"):
        edgelist = [
            (u, v, k)
            for u, v, k, d in graph.edges(keys=True, data=True)
            if d.get("relation") == relation
        ]
        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=edgelist,
            width=1.8,
            alpha=0.7,
            edge_color=_relation_color(relation),
            arrows=True,
            ax=ax,
        )

    ax.set_title(title)
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output


def draw_node_connections(
    graph: nx.MultiDiGraph,
    node_id: str,
    output_path: str | Path,
    include_reverse: bool = True,
) -> Path:
    subgraph = node_neighborhood_subgraph(graph, node_id, include_reverse=include_reverse)
    title = f"Neighborhood for {subgraph.nodes[node_id].get('label', node_id)}"
    return draw_graph(subgraph, output_path=output_path, title=title)
