#!/usr/bin/env python3
"""
Synchronize outputs/astronaut_data_mapping_v1_0/inference_chains_v1_0.json with the
authoritative integrated evidence graph.

The integrated evidence graph (integrated_evidence_graph_v1_0.json) is the single
source of truth. Every node of type "inference_chain" yields exactly one chain record
in the exported inference_chains_v1_0.json. This script reconstructs that exported file
deterministically from the graph, so the two artifacts can never silently drift.

Modes:
  (default)  Rebuild inference_chains_v1_0.json from the integrated graph and write it.
  --check    Do not write; exit non-zero if the on-disk export differs from what would
             be regenerated, or if any count is inconsistent.

Exits non-zero on any failure. Never fabricates chain content: every exported field is
copied verbatim from the corresponding inference_chain node in the integrated graph.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _project_paths import OUTPUTS_DIR  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("sync_inference_chains")

PKG_DIR = OUTPUTS_DIR / "astronaut_data_mapping_v1_0"
INTEGRATED_GRAPH = PKG_DIR / "integrated_evidence_graph_v1_0.json"
INFERENCE_CHAINS = PKG_DIR / "inference_chains_v1_0.json"

CHAIN_NODE_TYPE = "inference_chain"


def _first(seq: Any) -> str:
    if isinstance(seq, list) and seq:
        return str(seq[0])
    if isinstance(seq, str):
        return seq
    return ""


def load_integrated_graph(path: Path) -> dict[str, Any]:
    if not path.is_file():
        logger.error("Integrated graph not found: %s", path)
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "nodes" not in data:
        raise ValueError(f"Integrated graph malformed (missing 'nodes'): {path}")
    return data


def extract_chain_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = [n for n in graph.get("nodes", []) if n.get("type") == CHAIN_NODE_TYPE]
    logger.info("Found %d inference_chain nodes in integrated graph", len(nodes))
    if not nodes:
        raise ValueError("No inference_chain nodes found in integrated graph")
    return nodes


def node_to_chain_record(node: dict[str, Any]) -> dict[str, Any]:
    meta = node.get("metadata", {}) or {}
    chain_id = meta.get("chain_id") or str(node.get("id", "")).replace("chain::", "")
    if not chain_id:
        raise ValueError(f"inference_chain node without chain_id: {node.get('id')!r}")
    return {
        "chain_id": chain_id,
        "chain": node.get("description") or node.get("label") or "",
        "confidence": node.get("confidence", ""),
        "required_sources": list(meta.get("required_sources", []) or []),
        "source_file": _first(node.get("source_files")),
        "source_tree_id": _first(node.get("source_tree_ids")),
        "pattern_name": meta.get("pattern_name", ""),
        "not_a_diagnosis": meta.get("not_a_diagnosis", True),
        "output_type": meta.get("output_type", "traceable_inference_hypothesis"),
    }


def build_export(graph: dict[str, Any]) -> dict[str, Any]:
    chain_nodes = extract_chain_nodes(graph)
    records = [node_to_chain_record(n) for n in chain_nodes]

    ids = [r["chain_id"] for r in records]
    dupes = sorted({cid for cid in ids if ids.count(cid) > 1})
    if dupes:
        raise ValueError(f"Duplicate inference_chain chain_id(s): {dupes}")

    records.sort(key=lambda r: r["chain_id"])
    synthesis_status = (graph.get("metadata", {}) or {}).get(
        "synthesis_status", "assembled_from_existing_sources"
    )
    for rec in records:
        rec["synthesis_status"] = synthesis_status

    logger.info("Reconstructed %d chain records from integrated graph", len(records))
    return {
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "synthesis_status": synthesis_status,
        "total_chains": len(records),
        "inference_chains": records,
    }


def _comparable(export: dict[str, Any]) -> dict[str, Any]:
    """Strip volatile build_timestamp so --check compares content, not build time."""
    clone = dict(export)
    clone.pop("build_timestamp", None)
    return clone


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the on-disk export matches the integrated graph; do not write.",
    )
    args = parser.parse_args()

    graph = load_integrated_graph(INTEGRATED_GRAPH)
    rebuilt = build_export(graph)

    if args.check:
        if not INFERENCE_CHAINS.is_file():
            logger.error("Export missing for --check: %s", INFERENCE_CHAINS)
            return 1
        current = json.loads(INFERENCE_CHAINS.read_text(encoding="utf-8"))
        if _comparable(current) != _comparable(rebuilt):
            logger.error(
                "inference_chains_v1_0.json is OUT OF SYNC with the integrated graph. "
                "Run sync_inference_chains_v1_0.py (without --check) to regenerate."
            )
            cur_n = len(current.get("inference_chains", []))
            logger.error(
                "  on-disk records=%d total_chains=%s | graph-derived records=%d",
                cur_n,
                current.get("total_chains"),
                rebuilt["total_chains"],
            )
            return 1
        logger.info(
            "PASS: export is in sync (%d chains).", rebuilt["total_chains"]
        )
        return 0

    INFERENCE_CHAINS.write_text(
        json.dumps(rebuilt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    logger.info("Wrote %s (%d chains)", INFERENCE_CHAINS, rebuilt["total_chains"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
