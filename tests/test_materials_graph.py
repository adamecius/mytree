import importlib.util

import pytest

NETWORKX_INSTALLED = importlib.util.find_spec("networkx") is not None

pytestmark = pytest.mark.skipif(not NETWORKX_INSTALLED, reason="networkx is not installed")

if NETWORKX_INSTALLED:
    from kg.graph_build.materials_ontology import (
        Layer,
        RelationKind,
        build_materials_ontology_graph,
        edges_by_relation,
        node_neighborhood_subgraph,
        nodes_by_layer,
        validate_graph_structure,
    )


    def test_build_graph_has_three_layers() -> None:
        graph = build_materials_ontology_graph()
        assert len(nodes_by_layer(graph, Layer.PHYSICS)) > 0
        assert len(nodes_by_layer(graph, Layer.MATH)) > 0
        assert len(nodes_by_layer(graph, Layer.NUMERICS)) > 0


    def test_build_graph_has_expected_relation_families() -> None:
        graph = build_materials_ontology_graph()
        assert len(edges_by_relation(graph, RelationKind.APPROXIMATION_OF)) > 0
        assert len(edges_by_relation(graph, RelationKind.REPRESENTED_BY)) > 0
        assert len(edges_by_relation(graph, RelationKind.SOLVED_BY)) > 0


    def test_graph_validation_passes() -> None:
        graph = build_materials_ontology_graph()
        assert validate_graph_structure(graph) == []


    def test_node_neighborhood_contains_target() -> None:
        graph = build_materials_ontology_graph()
        subgraph = node_neighborhood_subgraph(graph, "phys:born_oppenheimer")
        assert "phys:born_oppenheimer" in subgraph.nodes
