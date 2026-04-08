from __future__ import annotations

import argparse

from kg.graph_build.materials_ontology import build_materials_ontology_graph, validate_graph_structure
from kg.graph_build.visualization import draw_graph, draw_node_connections


def main() -> None:
    parser = argparse.ArgumentParser(description="Materials ontology graph utilities")
    parser.add_argument("--draw-all", help="Path for full graph PNG output")
    parser.add_argument("--node-id", help="Node id for focused neighborhood view")
    parser.add_argument("--draw-node", help="Path for node neighborhood PNG output")
    parser.add_argument("--validate", action="store_true", help="Validate graph schema and edge layer semantics")
    args = parser.parse_args()

    graph = build_materials_ontology_graph()

    if args.validate:
        errors = validate_graph_structure(graph)
        if errors:
            print("Validation errors:")
            for err in errors:
                print(f"- {err}")
        else:
            print("Graph validation passed")

    if args.draw_all:
        out = draw_graph(graph, args.draw_all)
        print(f"Wrote full graph visualization to {out}")

    if args.node_id or args.draw_node:
        if not args.node_id or not args.draw_node:
            parser.error("--node-id and --draw-node must be used together")
        out = draw_node_connections(graph, node_id=args.node_id, output_path=args.draw_node)
        print(f"Wrote node neighborhood visualization to {out}")


if __name__ == "__main__":
    main()
