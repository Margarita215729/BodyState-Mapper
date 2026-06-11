#!/usr/bin/env python3
"""Query reachable hypotheses and evidence paths from observed input nodes."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from _project_paths import EDGES_JSON, GRAPH_JSON, NODES_JSON
from _static_graph import load_edges_json, load_graph_nodes_and_edges, load_nodes_json, query_graph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_start_nodes(start_arg: str | None, positional: list[str]) -> list[str]:
    nodes: list[str] = []
    if start_arg:
        nodes.extend(part.strip() for part in start_arg.split(",") if part.strip())
    for value in positional:
        value = value.strip()
        if value:
            nodes.append(value)
    if not nodes:
        raise ValueError("No start nodes provided. Use --start node_id,node_id")
    return nodes


def write_query_markdown(out_path: Path, result: dict) -> None:
    lines = [
        "# Static Graph Query Result v0.1",
        "",
        f"**Input nodes:** {', '.join(result['input_nodes'])}",
        f"**Max depth:** {result.get('max_depth', 4)}",
        "",
        "## Reachable summary",
        "",
        f"- Total reachable nodes: {len(result['reachable_nodes'])}",
        f"- Mechanisms: {len(result['reachable_mechanisms'])}",
        f"- Bridge nodes: {len(result['reachable_bridge_nodes'])}",
        f"- Risk states: {len(result['reachable_risk_states'])}",
        f"- State hypotheses: {len(result['reachable_psychological_state_hypotheses'])}",
        f"- Paths: {len(result['paths'])}",
        "",
    ]

    if result["reachable_mechanisms"]:
        lines.append("### Reachable mechanisms")
        for node in result["reachable_mechanisms"]:
            lines.append(f"- `{node}`")
        lines.append("")

    if result["reachable_bridge_nodes"]:
        lines.append("### Reachable bridge nodes")
        for node in result["reachable_bridge_nodes"]:
            lines.append(f"- `{node}`")
        lines.append("")

    if result["reachable_psychological_state_hypotheses"]:
        lines.append("### Reachable psychological state hypotheses")
        for node in result["reachable_psychological_state_hypotheses"]:
            lines.append(f"- `{node}`")
        lines.append("")

    lines.append("## Sample paths")
    lines.append("")
    for index, path_entry in enumerate(result["paths"][:10], start=1):
        sequence = " → ".join(path_entry["node_sequence"])
        lines.append(f"### Path {index}")
        lines.append(f"- **Sequence:** {sequence}")
        lines.append(f"- **Edges:** {', '.join(path_entry['edge_sequence'])}")
        lines.append(f"- **Sources:** {', '.join(path_entry['source_ids'])}")
        lines.append("")

    if len(result["paths"]) > 10:
        lines.append(f"_({len(result['paths']) - 10} additional paths omitted)_")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote query markdown to %s", out_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Query static evidence graph from observed node IDs."
    )
    parser.add_argument(
        "--start",
        dest="start_nodes",
        default=None,
        help="Comma-separated start node IDs for graph traversal.",
    )
    parser.add_argument(
        "node_ids",
        nargs="*",
        help="Optional additional start node IDs (space-separated).",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=4,
        help="Maximum traversal depth (default: 4).",
    )
    parser.add_argument(
        "--graph",
        type=Path,
        default=GRAPH_JSON,
        help="Built graph JSON path.",
    )
    parser.add_argument(
        "--nodes",
        type=Path,
        default=NODES_JSON,
        help="Nodes JSON path (fallback if graph missing).",
    )
    parser.add_argument(
        "--edges",
        type=Path,
        default=EDGES_JSON,
        help="Fallback edges JSON if graph file is missing.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON path (default: stdout).",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        default=None,
        help="Optional companion markdown summary path.",
    )
    args = parser.parse_args()

    try:
        input_nodes = parse_start_nodes(args.start_nodes, args.node_ids)

        if args.graph.is_file():
            nodes, edges, _graph = load_graph_nodes_and_edges(args.graph)
            logger.info("Loaded graph from %s", args.graph)
        else:
            nodes = load_nodes_json(args.nodes)
            edges = load_edges_json(args.edges)
            logger.warning("Graph artifact missing; using nodes/edges from data/")

        result = query_graph(
            input_nodes, edges, nodes, max_depth=args.max_depth
        )
        payload = json.dumps(result, indent=2)

        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload + "\n", encoding="utf-8")
            logger.info("Wrote query result to %s", args.output)
        else:
            print(payload)

        if args.markdown:
            write_query_markdown(args.markdown, result)

        logger.info(
            "Query complete: %d reachable nodes, %d mechanisms, "
            "%d hypotheses, %d paths",
            len(result["reachable_nodes"]),
            len(result["reachable_mechanisms"]),
            len(result["reachable_psychological_state_hypotheses"]),
            len(result["paths"]),
        )
        return 0

    except (ValueError, json.JSONDecodeError, FileNotFoundError) as exc:
        logger.error("Query failed: %s", exc)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
