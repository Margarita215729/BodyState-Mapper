#!/usr/bin/env python3
"""Build static nodes and the combined scientific evidence graph artifact."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from _project_paths import (
    EDGES_CSV,
    EDGES_JSON,
    GRAPH_JSON,
    NODES_CSV,
    NODES_JSON,
    NODES_MD,
    REGISTRY_CSV,
    REGISTRY_JSON,
)
from _static_graph import (
    build_graph_artifact,
    build_nodes,
    load_edges_csv,
    load_edges_json,
    load_registry_csv,
    load_registry_json,
    validate_static_graph,
    write_graph_json,
    write_nodes_csv,
    write_nodes_json,
    write_nodes_md,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build static nodes and evidence graph from registry and edges."
    )
    parser.add_argument(
        "--from-csv",
        action="store_true",
        help="Load registry and edges from CSV instead of JSON.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip post-build validation (not recommended).",
    )
    args = parser.parse_args()

    if args.from_csv:
        registry = load_registry_csv(REGISTRY_CSV)
        edges = load_edges_csv(EDGES_CSV)
    else:
        registry = load_registry_json(REGISTRY_JSON)
        edges = load_edges_json(EDGES_JSON)

    logger.info(
        "Loaded %d registry sources and %d edges",
        len(registry),
        len(edges),
    )

    if not edges:
        logger.warning(
            "Edges dataset is empty; graph will contain sources and nodes only."
        )

    nodes = build_nodes(edges, registry)

    write_nodes_csv(NODES_CSV, nodes)
    write_nodes_json(NODES_JSON, nodes)
    write_nodes_md(NODES_MD, nodes)

    validation_status = "passed"
    if not args.skip_validation:
        report = validate_static_graph(registry, edges, nodes)
        validation_status = "passed" if report.ok else "failed"
        if not report.ok:
            logger.warning(
                "Pre-build validation reported %d error(s); graph will still be written",
                len(report.errors),
            )

    graph = build_graph_artifact(
        registry, edges, nodes, validation_status=validation_status
    )
    write_graph_json(GRAPH_JSON, graph)

    logger.info(
        "Built graph artifact: %d nodes, %d edges, %d sources → %s",
        len(nodes),
        len(edges),
        len(registry),
        GRAPH_JSON,
    )

    if args.skip_validation:
        logger.warning("Skipping validation as requested.")
        return 0

    validate_script = Path(__file__).resolve().parent / "validate_static_graph.py"
    result = subprocess.run(
        [sys.executable, str(validate_script)],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
