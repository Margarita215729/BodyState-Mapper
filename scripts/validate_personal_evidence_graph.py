#!/usr/bin/env python3
"""Validate THSI Personal Evidence Graph v0.1 artifacts."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from _project_paths import (
    DEMO_INFERENCE_INPUT_FROM_PERSONAL_GRAPH,
    DEMO_PERSONAL_EVIDENCE_GRAPH,
    NODES_JSON,
)
from _static_graph import (
    infer_node_type,
    load_nodes_json,
    node_has_forbidden_clinical_token,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

RAW_REQUIRED_FIELDS = ("subject_id", "signal_type", "value", "quality_score")
DERIVED_REQUIRED_FIELDS = ("supporting_observations", "derived_node", "confidence", "quality_score")


def score_in_range(value: object, label: str, errors: list[str]) -> None:
    try:
        score = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        errors.append(f"{label}: score is not numeric ({value!r})")
        return
    if score < 0 or score > 1:
        errors.append(f"{label}: score {score} out of range [0, 1]")


def validate_personal_evidence_graph(
    personal_graph_path: Path,
    inference_input_path: Path,
    static_nodes_path: Path,
) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    passed: list[str] = []

    if not personal_graph_path.is_file():
        errors.append(f"Personal evidence graph JSON missing: {personal_graph_path}")
    if not inference_input_path.is_file():
        errors.append(f"Inference input JSON missing: {inference_input_path}")

    static_nodes = load_nodes_json(static_nodes_path)
    static_node_ids = {str(n["node_id"]) for n in static_nodes}

    personal_graph: dict[str, Any] = {}
    if personal_graph_path.is_file():
        try:
            personal_graph = json.loads(personal_graph_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid personal graph JSON: {exc}")
            personal_graph = {}

    inference_observations: list[dict[str, Any]] = []
    if inference_input_path.is_file():
        try:
            data = json.loads(inference_input_path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                errors.append("Inference input must be a JSON array")
            else:
                inference_observations = data
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid inference input JSON: {exc}")

    if personal_graph:
        raw_observations = personal_graph.get("raw_observations", [])
        if not isinstance(raw_observations, list):
            errors.append("raw_observations must be an array")
            raw_observations = []

        for index, obs in enumerate(raw_observations):
            prefix = f"raw_observations[{index}]"
            for field in RAW_REQUIRED_FIELDS:
                if field not in obs or obs[field] is None:
                    errors.append(f"{prefix}: missing required field '{field}'")
            score_in_range(obs.get("quality_score"), f"{prefix}.quality_score", errors)

        if raw_observations and not any(
            f"missing required field" in e for e in errors if "raw_observations" in e
        ):
            passed.append(
                f"All {len(raw_observations)} raw observations have required fields"
            )

        derived_markers = personal_graph.get("derived_markers", [])
        if not isinstance(derived_markers, list):
            errors.append("derived_markers must be an array")
            derived_markers = []

        for index, marker in enumerate(derived_markers):
            prefix = f"derived_markers[{index}]"
            supporting = marker.get("supporting_observations", [])
            if not supporting:
                errors.append(f"{prefix}: missing supporting_observations")
            for field in DERIVED_REQUIRED_FIELDS:
                if field == "supporting_observations":
                    continue
                if field not in marker or marker[field] is None:
                    errors.append(f"{prefix}: missing required field '{field}'")

            derived_node = str(marker.get("derived_node", "")).strip()
            if derived_node and derived_node not in static_node_ids:
                if derived_node not in ("illness_symptoms_present", "recent_exercise_context"):
                    errors.append(
                        f"{prefix}: derived_node '{derived_node}' not in static_nodes_v0_1.json"
                    )

            if node_has_forbidden_clinical_token(derived_node):
                errors.append(
                    f"{prefix}: derived_node '{derived_node}' maps to forbidden clinical token"
                )

            node_type = infer_node_type(derived_node)
            if node_type == "psychological_state_hypothesis":
                errors.append(
                    f"{prefix}: derived_node '{derived_node}' maps directly to "
                    "psychological state hypothesis"
                )

            score_in_range(marker.get("confidence"), f"{prefix}.confidence", errors)
            score_in_range(marker.get("quality_score"), f"{prefix}.quality_score", errors)

            baseline_used = marker.get("baseline_used")
            if baseline_used is not None and isinstance(baseline_used, dict):
                if baseline_used.get("sample_count") is None:
                    errors.append(
                        f"{prefix}: baseline_used missing sample_count when baseline applied"
                    )

        if derived_markers and not any(
            "missing supporting_observations" in e for e in errors
        ):
            passed.append(
                f"All {len(derived_markers)} derived markers have supporting_observations"
            )

        matched = personal_graph.get("matched_static_nodes", [])
        if isinstance(matched, list):
            for node_id in matched:
                if str(node_id) not in static_node_ids:
                    errors.append(
                        f"matched_static_nodes contains unknown node '{node_id}'"
                    )

    for index, obs in enumerate(inference_observations):
        prefix = f"inference_input[{index}]"
        observed_node = str(obs.get("observed_node", "")).strip()
        if observed_node not in static_node_ids:
            errors.append(
                f"{prefix}: observed_node '{observed_node}' not in static graph"
            )
        score_in_range(obs.get("quality_score"), f"{prefix}.quality_score", errors)

    if inference_observations and not any("inference_input" in e for e in errors):
        passed.append(
            f"All {len(inference_observations)} inference input observations reference static nodes"
        )

    if personal_graph_path.is_file():
        passed.append(f"Personal evidence graph JSON exists: {personal_graph_path}")
    if inference_input_path.is_file():
        passed.append(f"Inference input JSON exists: {inference_input_path}")

    ok = len(errors) == 0
    return ok, errors, passed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate personal evidence graph and inference input artifacts."
    )
    parser.add_argument(
        "--personal-graph",
        type=Path,
        default=DEMO_PERSONAL_EVIDENCE_GRAPH,
    )
    parser.add_argument(
        "--inference-input",
        type=Path,
        default=DEMO_INFERENCE_INPUT_FROM_PERSONAL_GRAPH,
    )
    parser.add_argument("--static-nodes", type=Path, default=NODES_JSON)
    args = parser.parse_args()

    ok, errors, passed = validate_personal_evidence_graph(
        args.personal_graph,
        args.inference_input,
        args.static_nodes,
    )

    print("=== THSI Personal Evidence Graph Validation ===")
    print()
    if passed:
        print(f"Passed ({len(passed)}):")
        for item in passed:
            print(f"  ✓ {item}")
        print()

    if ok:
        print("Validation status: PASSED")
        logger.info("Personal evidence graph validation passed")
        return 0

    print("Validation status: FAILED")
    print(f"Errors ({len(errors)}):")
    for item in errors:
        print(f"  ✗ {item}")
        logger.error("Validation error: %s", item)
    return 1


if __name__ == "__main__":
    sys.exit(main())
