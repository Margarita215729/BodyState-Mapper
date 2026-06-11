#!/usr/bin/env python3
"""Validate THSI Inference Engine v0.1 JSON and Markdown outputs."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from _project_paths import DEMO_INFERENCE_JSON, DEMO_INFERENCE_MD
from _static_graph import (
    infer_node_type,
    node_has_forbidden_clinical_token,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def score_in_range(value: object, label: str, errors: list[str]) -> None:
    try:
        score = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        errors.append(f"{label}: score is not numeric ({value!r})")
        return
    if score < 0 or score > 1:
        errors.append(f"{label}: score {score} out of range [0, 1]")


def validate_inference_json(data: dict, errors: list[str]) -> None:
    hypotheses = data.get("hypotheses", [])
    if not isinstance(hypotheses, list):
        errors.append("hypotheses must be an array")
        return

    for index, hyp in enumerate(hypotheses):
        prefix = f"hypotheses[{index}]"
        supporting = hyp.get("supporting_paths", [])
        if not supporting:
            errors.append(f"{prefix}: hypothesis has no supporting paths")

        limitations = hyp.get("limitations", [])
        if not limitations:
            errors.append(f"{prefix}: hypothesis has no limitations")

        if hyp.get("not_diagnostic_warning") is not True:
            errors.append(f"{prefix}: not_diagnostic_warning must be true")

        score_in_range(
            hyp.get("hypothesis_score"),
            f"{prefix}.hypothesis_score",
            errors,
        )

        for p_index, path in enumerate(supporting):
            path_prefix = f"{prefix}.supporting_paths[{p_index}]"
            source_ids = path.get("source_ids", [])
            if not source_ids:
                errors.append(f"{path_prefix}: path has no source_ids")

            score_in_range(path.get("path_score"), f"{path_prefix}.path_score", errors)

            node_sequence = path.get("node_sequence", [])
            for node_id in node_sequence:
                if node_has_forbidden_clinical_token(str(node_id)):
                    errors.append(
                        f"{path_prefix}: forbidden clinical token in node '{node_id}'"
                    )

            if len(node_sequence) == 2:
                source_type = infer_node_type(str(node_sequence[0]))
                target_type = infer_node_type(str(node_sequence[-1]))
                if (
                    source_type == "observable_marker"
                    and target_type == "psychological_state_hypothesis"
                ):
                    errors.append(
                        f"{path_prefix}: forbidden direct observable_marker → "
                        f"psychological_state_hypothesis path"
                    )

            for component in path.get("score_components", []):
                score_in_range(
                    component.get("edge_score"),
                    f"{path_prefix}.score_components.edge_score",
                    errors,
                )

    all_paths = data.get("all_evidence_paths", [])
    if isinstance(all_paths, list):
        for index, path in enumerate(all_paths):
            path_prefix = f"all_evidence_paths[{index}]"
            if not path.get("source_ids"):
                errors.append(f"{path_prefix}: path has no source_ids")
            score_in_range(path.get("path_score"), f"{path_prefix}.path_score", errors)


def validate_inference_output(json_path: Path, markdown_path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if not json_path.is_file():
        errors.append(f"JSON output missing: {json_path}")
    if not markdown_path.is_file():
        errors.append(f"Markdown report missing: {markdown_path}")

    if json_path.is_file():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON: {exc}")
            data = {}
        if isinstance(data, dict):
            validate_inference_json(data, errors)

    ok = len(errors) == 0
    return ok, errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate THSI inference JSON and Markdown outputs."
    )
    parser.add_argument("--json", type=Path, default=DEMO_INFERENCE_JSON)
    parser.add_argument("--markdown", type=Path, default=DEMO_INFERENCE_MD)
    args = parser.parse_args()

    ok, errors = validate_inference_output(args.json, args.markdown)

    print("=== THSI Inference Output Validation ===")
    print()
    if ok:
        print("Validation status: PASSED")
        logger.info("Inference output validation passed")
        return 0

    print("Validation status: FAILED")
    print(f"Errors ({len(errors)}):")
    for item in errors:
        print(f"  ✗ {item}")
        logger.error("Validation error: %s", item)
    return 1


if __name__ == "__main__":
    sys.exit(main())
