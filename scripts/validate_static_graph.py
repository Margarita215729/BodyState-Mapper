#!/usr/bin/env python3
"""Validate registry, edges, nodes, and PDF alignment for the static evidence graph."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from _project_paths import (
    EDGES_CSV,
    EDGES_JSON,
    GRAPH_JSON,
    NODES_JSON,
    REGISTRY_CSV,
    REGISTRY_JSON,
    SOURCES_PDF_DIR,
)
from _static_graph import (
    build_nodes,
    load_edges_csv,
    load_edges_json,
    load_nodes_json,
    load_registry_csv,
    load_registry_json,
    print_validation_report,
    validate_static_graph,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate THSI static scientific evidence graph data."
    )
    parser.add_argument(
        "--from-csv",
        action="store_true",
        help="Load registry and edges from CSV instead of JSON.",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=REGISTRY_JSON,
        help="Registry JSON path.",
    )
    parser.add_argument(
        "--edges",
        type=Path,
        default=EDGES_JSON,
        help="Edges JSON path.",
    )
    parser.add_argument(
        "--nodes",
        type=Path,
        default=NODES_JSON,
        help="Nodes JSON path (built if missing).",
    )
    parser.add_argument(
        "--pdf-dir",
        type=Path,
        default=SOURCES_PDF_DIR,
        help="Directory containing source PDFs.",
    )
    parser.add_argument(
        "--graph",
        type=Path,
        default=GRAPH_JSON,
        help="Optional built graph JSON to cross-check counts.",
    )
    args = parser.parse_args()
    report = None

    try:
        if args.from_csv:
            registry_path = REGISTRY_CSV if args.registry == REGISTRY_JSON else args.registry
            edges_path = EDGES_CSV if args.edges == EDGES_JSON else args.edges
            registry = load_registry_csv(registry_path)
            edges = load_edges_csv(edges_path)
        else:
            registry = load_registry_json(args.registry)
            edges = load_edges_json(args.edges)

        if args.nodes.is_file():
            nodes = load_nodes_json(args.nodes)
        else:
            nodes = build_nodes(edges, registry)
            logger.info("Nodes file missing; inferred %d nodes from edges", len(nodes))

        logger.info(
            "Loaded %d registry entries, %d edges, %d nodes",
            len(registry),
            len(edges),
            len(nodes),
        )

        report = validate_static_graph(
            registry, edges, nodes, pdf_dir=args.pdf_dir
        )

        if args.graph.is_file():
            graph = json.loads(args.graph.read_text(encoding="utf-8"))
            summary = graph.get("validation_summary", {})
            for key, expected in (
                ("node_count", len(nodes)),
                ("edge_count", len(edges)),
                ("source_count", len(registry)),
            ):
                actual = summary.get(key)
                if actual != expected:
                    report.errors.append(
                        f"graph validation_summary.{key}={actual} "
                        f"does not match expected {expected}"
                    )

        print_validation_report(report)

    except (ValueError, json.JSONDecodeError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if report is None or not report.ok:
        logger.error(
            "Validation failed with %d error(s)",
            len(report.errors) if report else 1,
        )
        return 1

    logger.info("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
