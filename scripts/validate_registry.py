#!/usr/bin/env python3
"""
Validate evidence source registry and static scientific edges against JSON schemas
and THSI graph rules.

Exits with non-zero code on validation failure.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

from _project_paths import (
    EDGE_FIELDS,
    EDGES_CSV,
    EDGES_JSON,
    EVIDENCE_SOURCE_SCHEMA,
    REGISTRY_CSV,
    REGISTRY_FIELDS,
    REGISTRY_JSON,
    STATIC_EDGE_SCHEMA,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

FORBIDDEN_TARGET_EXACT = {
    "depression_diagnosis",
    "anxiety_diagnosis",
    "panic_attack",
    "chronic_stress_diagnosis",
    "bipolar_diagnosis",
    "ptsd_diagnosis",
    "adhd_diagnosis",
}

FORBIDDEN_TARGET_SUFFIXES = ("_diagnosis", "_disorder_diagnosis", "_clinical_diagnosis")

BIOMARKER_SOURCE_HINTS = (
    "hrv",
    "eda",
    "cortisol",
    "heart_rate",
    "sleep_loss",
    "resting_hrv",
    "sympathetic",
    "parasympathetic",
    "galvanic",
    "skin_conductance",
)

SOURCE_REQUIRED_FIELDS = (
    "source_id",
    "title",
    "source_type",
    "domain",
    "evidence_strength_score",
    "risk_of_overinterpretation",
)

EDGE_REQUIRED_FIELDS = (
    "edge_id",
    "source_node",
    "target_node",
    "relationship_type",
    "evidence_strength_score",
    "source_ids",
    "domain",
    "risk_of_overinterpretation",
)


class ValidationError(Exception):
    """Collect validation errors."""

    def __init__(self, messages: list[str]) -> None:
        self.messages = messages
        super().__init__("\n".join(messages))


def load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def get_jsonschema_validator():
    try:
        import jsonschema  # type: ignore

        return jsonschema
    except ImportError:
        return None


def load_registry_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValidationError([f"Registry JSON must be an array: {path}"])
    return data


def load_registry_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for row in reader:
            if not any(v.strip() for v in row.values() if v):
                continue
            item = dict(row)
            if item.get("year"):
                try:
                    item["year"] = int(item["year"])
                except ValueError:
                    pass
            if item.get("evidence_strength_score"):
                try:
                    item["evidence_strength_score"] = int(item["evidence_strength_score"])
                except ValueError:
                    pass
            rows.append(item)
        return rows


def load_edges_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValidationError([f"Edges JSON must be an array: {path}"])
    return data


def parse_source_ids(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    text = str(raw).strip()
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def load_edges_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for row in reader:
            if not any(v.strip() for v in row.values() if v):
                continue
            item = dict(row)
            item["source_ids"] = parse_source_ids(item.get("source_ids", ""))
            if item.get("evidence_strength_score"):
                try:
                    item["evidence_strength_score"] = int(item["evidence_strength_score"])
                except ValueError:
                    pass
            rows.append(item)
        return rows


def is_forbidden_diagnostic_target(target_node: str) -> bool:
    normalized = target_node.strip().lower()
    if normalized in FORBIDDEN_TARGET_EXACT:
        return True
    return any(normalized.endswith(suffix) for suffix in FORBIDDEN_TARGET_SUFFIXES)


def looks_like_biomarker_source(source_node: str) -> bool:
    normalized = source_node.strip().lower()
    return any(hint in normalized for hint in BIOMARKER_SOURCE_HINTS)


def validate_with_jsonschema(
    items: list[dict[str, Any]],
    schema: dict[str, Any],
    label: str,
    jsonschema_mod: Any,
) -> list[str]:
    errors: list[str] = []
    validator_cls = jsonschema_mod.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    validator = validator_cls(schema)
    for index, item in enumerate(items):
        for error in sorted(validator.iter_errors(item), key=lambda e: e.path):
            path = ".".join(str(p) for p in error.path) or "(root)"
            errors.append(f"{label}[{index}] {path}: {error.message}")
    return errors


def basic_validate_registry_item(item: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    prefix = f"registry[{index}]"
    for field in SOURCE_REQUIRED_FIELDS:
        value = item.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"{prefix}: missing required field '{field}'")
    score = item.get("evidence_strength_score")
    if score is not None:
        try:
            score_int = int(score)
            if score_int < 1 or score_int > 5:
                errors.append(f"{prefix}: evidence_strength_score must be 1-5")
        except (TypeError, ValueError):
            errors.append(f"{prefix}: evidence_strength_score must be integer 1-5")
    risk = item.get("risk_of_overinterpretation")
    if risk and risk not in {"low", "medium", "high", "critical"}:
        errors.append(f"{prefix}: invalid risk_of_overinterpretation '{risk}'")
    return errors


def basic_validate_edge_item(item: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    prefix = f"edge[{index}] edge_id={item.get('edge_id', '?')}"
    for field in EDGE_REQUIRED_FIELDS:
        value = item.get(field)
        if field == "source_ids":
            ids = parse_source_ids(value)
            if not ids:
                errors.append(f"{prefix}: must have at least one source_id")
            continue
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"{prefix}: missing required field '{field}'")

    source_node = str(item.get("source_node", ""))
    target_node = str(item.get("target_node", ""))
    if is_forbidden_diagnostic_target(target_node):
        errors.append(
            f"{prefix}: forbidden direct diagnostic edge "
            f"({source_node} → {target_node}). "
            "Psychological/clinical diagnoses must not be direct targets from observables."
        )
    elif looks_like_biomarker_source(source_node) and target_node.endswith("_hypothesis"):
        errors.append(
            f"{prefix}: suspicious direct biomarker → psychological hypothesis "
            f"({source_node} → {target_node}); require intermediate mechanism nodes."
        )

    risk = item.get("risk_of_overinterpretation")
    if risk and risk not in {"low", "medium", "high", "critical"}:
        errors.append(f"{prefix}: invalid risk_of_overinterpretation '{risk}'")
    return errors


def validate_source_id_references(
    edges: list[dict[str, Any]], registry_ids: set[str]
) -> list[str]:
    errors: list[str] = []
    for index, edge in enumerate(edges):
        for source_id in parse_source_ids(edge.get("source_ids")):
            if source_id not in registry_ids:
                errors.append(
                    f"edge[{index}] edge_id={edge.get('edge_id', '?')}: "
                    f"unknown source_id '{source_id}' not in registry"
                )
    return errors


def validate_registry(
    registry: list[dict[str, Any]], jsonschema_mod: Any | None
) -> list[str]:
    errors: list[str] = []
    if jsonschema_mod is not None:
        schema = load_schema(EVIDENCE_SOURCE_SCHEMA)
        errors.extend(
            validate_with_jsonschema(registry, schema, "registry", jsonschema_mod)
        )
    for index, item in enumerate(registry):
        errors.extend(basic_validate_registry_item(item, index))
    return errors


def validate_edges(
    edges: list[dict[str, Any]],
    registry_ids: set[str],
    jsonschema_mod: Any | None,
) -> list[str]:
    errors: list[str] = []
    if jsonschema_mod is not None:
        schema = load_schema(STATIC_EDGE_SCHEMA)
        errors.extend(validate_with_jsonschema(edges, schema, "edge", jsonschema_mod))
    for index, item in enumerate(edges):
        errors.extend(basic_validate_edge_item(item, index))
    errors.extend(validate_source_id_references(edges, registry_ids))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate THSI evidence registry and static edges."
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=REGISTRY_JSON,
        help="Registry JSON path (default: data/evidence_source_registry_v0_1.json).",
    )
    parser.add_argument(
        "--edges",
        type=Path,
        default=EDGES_JSON,
        help="Edges JSON path (default: data/static_scientific_edges_v0_1.json).",
    )
    parser.add_argument(
        "--from-csv",
        action="store_true",
        help="Load registry and edges from CSV instead of JSON.",
    )
    args = parser.parse_args()

    jsonschema_mod = get_jsonschema_validator()
    if jsonschema_mod is None:
        logger.warning(
            "jsonschema package not installed; using basic validation only."
        )
    else:
        logger.info("Using jsonschema for schema validation.")

    all_errors: list[str] = []

    try:
        if args.from_csv:
            registry_path = REGISTRY_CSV if args.registry == REGISTRY_JSON else args.registry
            edges_path = EDGES_CSV if args.edges == EDGES_JSON else args.edges
            registry = load_registry_csv(registry_path)
            edges = load_edges_csv(edges_path)
        else:
            registry = load_registry_json(args.registry)
            edges = load_edges_json(args.edges)

        logger.info("Loaded %d registry entries, %d edges", len(registry), len(edges))

        all_errors.extend(validate_registry(registry, jsonschema_mod))
        registry_ids = {
            str(item["source_id"]).strip()
            for item in registry
            if item.get("source_id")
        }
        all_errors.extend(validate_edges(edges, registry_ids, jsonschema_mod))

    except ValidationError as exc:
        all_errors.extend(exc.messages)
    except FileNotFoundError as exc:
        all_errors.append(f"File not found: {exc}")
    except json.JSONDecodeError as exc:
        all_errors.append(f"Invalid JSON: {exc}")

    if all_errors:
        logger.error("Validation failed with %d error(s):", len(all_errors))
        for message in all_errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1

    logger.info("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
