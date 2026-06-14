#!/usr/bin/env python3
"""
Validate data/source_claim_registry_v1_0.json.

Checks:
  - File exists and is valid JSON with metadata + source_claims.
  - Conforms to schemas/source_claim_registry_v1_0.schema.json (if jsonschema present).
  - Every source_id resolves to an entry in the evidence source registry.
  - Every supported_node_id resolves to a curated static node.
  - Every supported_edge_id resolves to a curated static edge.
  - metadata.total_sources == number of source_claims.
  - metadata.total_claims == sum of per-source claim counts.
  - claim_count (when present) matches len(claims).
  - No claim text is empty.
  - An empty source_claims array is accepted ONLY as an initial scaffold (metadata must
    declare total_claims == 0); a populated registry must be internally consistent.

Exits non-zero on any failure.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _project_paths import DATA_DIR, SCHEMAS_DIR  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("validate_source_claim_registry")

REGISTRY_FILE = DATA_DIR / "source_claim_registry_v1_0.json"
SCHEMA_FILE = SCHEMAS_DIR / "source_claim_registry_v1_0.schema.json"
EVIDENCE_REGISTRY = DATA_DIR / "evidence_source_registry_v0_1.json"
STATIC_NODES = DATA_DIR / "static_nodes_v0_1.json"
STATIC_EDGES = DATA_DIR / "static_scientific_edges_v0_1.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def get_jsonschema():
    try:
        import jsonschema  # type: ignore

        return jsonschema
    except ImportError:
        return None


def validate() -> list[str]:
    errors: list[str] = []

    if not REGISTRY_FILE.is_file():
        return [f"Source-claim registry not found: {REGISTRY_FILE}"]

    try:
        data = load_json(REGISTRY_FILE)
    except json.JSONDecodeError as exc:
        return [f"Invalid JSON in {REGISTRY_FILE}: {exc}"]

    if not isinstance(data, dict) or "metadata" not in data or "source_claims" not in data:
        return ["Registry must be an object with 'metadata' and 'source_claims'."]

    metadata = data["metadata"]
    claims = data["source_claims"]

    jsonschema_mod = get_jsonschema()
    if jsonschema_mod is not None and SCHEMA_FILE.is_file():
        schema = load_json(SCHEMA_FILE)
        validator_cls = jsonschema_mod.validators.validator_for(schema)
        validator_cls.check_schema(schema)
        validator = validator_cls(schema)
        for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
            path = ".".join(str(p) for p in err.path) or "(root)"
            errors.append(f"schema {path}: {err.message}")
    elif jsonschema_mod is None:
        logger.warning("jsonschema not installed; skipping schema conformance check.")

    known_sources = {
        s["source_id"] for s in load_json(EVIDENCE_REGISTRY) if s.get("source_id")
    }
    known_nodes = {n["node_id"] for n in load_json(STATIC_NODES) if n.get("node_id")}
    known_edges = {e["edge_id"] for e in load_json(STATIC_EDGES) if e.get("edge_id")}

    total_claims = 0
    for idx, claim in enumerate(claims):
        prefix = f"source_claims[{idx}] source_id={claim.get('source_id', '?')}"
        sid = claim.get("source_id")
        if sid not in known_sources:
            errors.append(f"{prefix}: source_id not in evidence registry")
        for nid in claim.get("supported_node_ids", []):
            if nid not in known_nodes:
                errors.append(f"{prefix}: supported_node_id '{nid}' not a static node")
        for eid in claim.get("supported_edge_ids", []):
            if eid not in known_edges:
                errors.append(f"{prefix}: supported_edge_id '{eid}' not a static edge")
        claim_texts = claim.get("claims", [])
        for j, text in enumerate(claim_texts):
            if not str(text).strip():
                errors.append(f"{prefix}: claims[{j}] is empty")
        declared = claim.get("claim_count")
        if declared is not None and declared != len(claim_texts):
            errors.append(
                f"{prefix}: claim_count {declared} != len(claims) {len(claim_texts)}"
            )
        total_claims += len(claim_texts)

    declared_sources = metadata.get("total_sources")
    if declared_sources != len(claims):
        errors.append(
            f"metadata.total_sources {declared_sources} != number of source_claims "
            f"{len(claims)}"
        )
    declared_total_claims = metadata.get("total_claims")
    if declared_total_claims != total_claims:
        errors.append(
            f"metadata.total_claims {declared_total_claims} != actual claim total "
            f"{total_claims}"
        )

    if not claims:
        if metadata.get("total_claims") not in (0, None):
            errors.append(
                "Empty source_claims is only allowed as a scaffold (total_claims must be 0)."
            )
        else:
            logger.info("Registry is an empty scaffold (accepted as initial state).")

    return errors


def main() -> int:
    logger.info("Validating source-claim registry: %s", REGISTRY_FILE)
    errors = validate()
    if errors:
        logger.error("Validation FAILED with %d error(s):", len(errors))
        for msg in errors:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 1
    logger.info("Validation PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
