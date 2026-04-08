# KG graph_build module

## Why this module exists
This folder contains the concrete layered ontology implementation for physics/math/numerics and utilities to inspect/visualize it.

## Files
- `materials_ontology.py`: enums, dataclasses, graph builder, validators, and graph query helpers.
- `visualization.py`: matplotlib-based rendering helpers for full graph and node neighborhoods.
- `cli.py`: command line interface to validate and render graphs.
- `__init__.py`: public exports for graph-build APIs.

## Function one-liners
- `build_materials_ontology_graph()`: constructs and populates the full typed ontology graph.
- `validate_graph_structure(graph)`: checks layer-kind consistency and valid layer relation pairs.
- `nodes_by_layer(graph, layer)`: lists nodes belonging to a specific ontology layer.
- `edges_by_relation(graph, relation)`: lists edges for a given semantic relation type.
- `layered_positions(graph)`: computes deterministic layered coordinates for plotting.
- `node_neighborhood_subgraph(graph, node_id)`: returns a local subgraph around one node.
- `draw_graph(graph, output_path, title)`: renders the full graph to PNG.
- `draw_node_connections(graph, node_id, output_path)`: renders local neighborhood for one node.
- `main()`: CLI entrypoint for validate/draw workflows.
