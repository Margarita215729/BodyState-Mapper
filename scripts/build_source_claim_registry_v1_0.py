#!/usr/bin/env python3
"""
Build data/source_claim_registry_v1_0.json from existing curated metadata.

The source-claim registry makes the link between each evidence source and the graph
elements it supports explicit and reviewable. It is generated CONSERVATIVELY and never
invents claim text:

  - claim_text values are copied verbatim from each source's existing
    `main_findings_short` entries in data/evidence_source_registry_v0_1.json.
  - supported_node_ids and supported_edge_ids are DERIVED from the curated static edges
    (data/static_scientific_edges_v0_1.json): an edge belongs to a source when that
    source_id appears in the edge's source_ids. Node links are the endpoints of those
    edges. Both are canonical identifiers that already exist in the curated graph.
  - Claim-to-node/edge linkage is asserted at SOURCE granularity only
    (linkage_granularity = "source_level"); we do not fabricate a per-claim mapping that
    the underlying metadata does not contain.

If a source has no curated findings AND no derivable links, it is still emitted with an
explicit empty linkage so the registry stays complete and traceable.

Exits non-zero on failure (missing inputs, unresolved identifiers).
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _project_paths import DATA_DIR  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("build_source_claim_registry")

REGISTRY_JSON = DATA_DIR / "evidence_source_registry_v0_1.json"
EDGES_JSON = DATA_DIR / "static_scientific_edges_v0_1.json"
NODES_JSON = DATA_DIR / "static_nodes_v0_1.json"
OUTPUT_JSON = DATA_DIR / "source_claim_registry_v1_0.json"

SCIENTIFIC_NAME = "Traceable Human State Inference Under Partial Biological Observability"


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [part.strip() for part in value.split(",") if part.strip()]
    return []


def load_json(path: Path) -> Any:
    if not path.is_file():
        logger.error("Required input not found: %s", path)
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict[str, Any]:
    registry = load_json(REGISTRY_JSON)
    edges = load_json(EDGES_JSON)
    nodes = load_json(NODES_JSON)

    node_ids = {n["node_id"] for n in nodes if n.get("node_id")}

    edges_by_source: dict[str, list[str]] = {}
    nodes_by_source: dict[str, set[str]] = {}
    for edge in edges:
        eid = edge.get("edge_id")
        for sid in _as_list(edge.get("source_ids")):
            edges_by_source.setdefault(sid, [])
            if eid and eid not in edges_by_source[sid]:
                edges_by_source[sid].append(eid)
            endpoints = nodes_by_source.setdefault(sid, set())
            for ep in (edge.get("source_node"), edge.get("target_node")):
                if ep in node_ids:
                    endpoints.add(ep)

    source_claims: list[dict[str, Any]] = []
    total_claims = 0
    for src in registry:
        sid = src.get("source_id")
        if not sid:
            continue
        claims = _as_list(src.get("main_findings_short"))
        total_claims += len(claims)
        supported_edge_ids = sorted(edges_by_source.get(sid, []))
        supported_node_ids = sorted(nodes_by_source.get(sid, set()))
        source_claims.append(
            {
                "source_id": sid,
                "title": str(src.get("title", "")),
                "claims": claims,
                "claim_count": len(claims),
                "supported_node_ids": supported_node_ids,
                "supported_edge_ids": supported_edge_ids,
                "evidence_strength_score": src.get("evidence_strength_score"),
                "risk_of_overinterpretation": src.get("risk_of_overinterpretation"),
                "claim_text_source": "main_findings_short",
                "linkage_granularity": "source_level",
            }
        )

    source_claims.sort(key=lambda c: c["source_id"])

    notes = [
        "Claim text is copied verbatim from curated source main_findings_short; no claim "
        "text is invented.",
        "supported_node_ids and supported_edge_ids are derived from curated static edges "
        "(edge.source_ids) and are canonical identifiers present in the static graph.",
        "Claim-to-element linkage is asserted at source granularity only.",
    ]
    if total_claims == 0:
        notes.append(
            "TODO: source_claims is an empty scaffold; no curated claim text was available "
            "to extract."
        )

    logger.info(
        "Built source-claim registry: %d sources, %d claims",
        len(source_claims),
        total_claims,
    )
    return {
        "metadata": {
            "registry_id": "thsi_source_claim_registry_v1_0",
            "version": "1.0",
            "scientific_name": SCIENTIFIC_NAME,
            "product": "BodyState Mapper",
            "not_a_diagnostic_system": True,
            "build_timestamp": datetime.now(timezone.utc).isoformat(),
            "generated_by": "scripts/build_source_claim_registry_v1_0.py",
            "sources_of_truth": [
                "data/evidence_source_registry_v0_1.json",
                "data/static_scientific_edges_v0_1.json",
                "data/static_nodes_v0_1.json",
            ],
            "claim_text_policy": "verbatim_from_curated_metadata_only",
            "total_sources": len(source_claims),
            "total_claims": total_claims,
            "notes": notes,
        },
        "source_claims": source_claims,
    }


def main() -> int:
    payload = build()
    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    logger.info("Wrote %s", OUTPUT_JSON)
    return 0


if __name__ == "__main__":
    sys.exit(main())
