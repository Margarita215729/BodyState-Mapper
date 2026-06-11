#!/usr/bin/env python3
"""Build a personal evidence graph from raw observations and personal baseline."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from _project_paths import (
    DEMO_INFERENCE_INPUT_FROM_PERSONAL_GRAPH,
    DEMO_PERSONAL_BASELINE,
    DEMO_PERSONAL_EVIDENCE_GRAPH,
    DEMO_PERSONAL_EVIDENCE_GRAPH_REPORT,
    DEMO_RAW_OBSERVATIONS,
    GRAPH_JSON,
    PERSONAL_GRAPH_ID,
)
from _static_graph import (
    infer_node_type,
    load_graph_nodes_and_edges,
    node_has_forbidden_clinical_token,
    node_id_to_label,
)
from map_observations_to_nodes import (
    CONTEXT_ONLY_DERIVED_NODES,
    derived_markers_to_inference_observations,
    map_observations_to_derived_markers,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_WARNINGS = [
    "This is not a medical diagnosis.",
    "Mapping rules are preliminary and rule-based only.",
    "Baseline quality affects confidence scores.",
    "Additional context may change interpretation.",
]


def load_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_raw_observations(path: Path) -> list[dict[str, Any]]:
    data = load_json_file(path)
    if not isinstance(data, list):
        raise ValueError(f"Raw observations must be a JSON array: {path}")
    return data


def load_personal_baseline(path: Path) -> dict[str, Any]:
    data = load_json_file(path)
    if not isinstance(data, dict):
        raise ValueError(f"Personal baseline must be a JSON object: {path}")
    return data


def validate_derived_nodes_in_static_graph(
    derived_markers: list[dict[str, Any]],
    static_node_ids: set[str],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for marker in derived_markers:
        derived_node = str(marker.get("derived_node", "")).strip()
        if derived_node in CONTEXT_ONLY_DERIVED_NODES:
            if derived_node not in static_node_ids:
                warnings.append(
                    f"Context-only derived_node '{derived_node}' is not in static graph; "
                    "excluded from inference input."
                )
            continue
        if derived_node not in static_node_ids:
            errors.append(
                f"derived_node '{derived_node}' (marker {marker.get('marker_id')}) "
                "not found in static graph nodes"
            )
    return errors, warnings


def build_matched_static_nodes(
    derived_markers: list[dict[str, Any]],
    static_node_ids: set[str],
) -> list[str]:
    matched: set[str] = set()
    for marker in derived_markers:
        derived_node = str(marker.get("derived_node", "")).strip()
        if derived_node in static_node_ids and derived_node not in CONTEXT_ONLY_DERIVED_NODES:
            matched.add(derived_node)
    return sorted(matched)


def write_markdown_report(
    path: Path,
    *,
    raw_observations: list[dict[str, Any]],
    baseline: dict[str, Any],
    derived_markers: list[dict[str, Any]],
    matched_nodes: list[str],
    inference_observations: list[dict[str, Any]],
    warnings: list[str],
) -> None:
    lines = [
        "# Personal Evidence Graph Demo v0.1",
        "",
        "## Raw observations",
        "",
    ]

    for obs in raw_observations:
        lines.extend(
            [
                f"### {obs.get('observation_id')}",
                f"- **Signal:** `{obs.get('signal_type')}`",
                f"- **Value:** {json.dumps(obs.get('value'))} {obs.get('unit') or ''}".strip(),
                f"- **Source:** {obs.get('source')}",
                f"- **Quality score:** {obs.get('quality_score')}",
                f"- **Notes:** {obs.get('notes', '')}",
                "",
            ]
        )

    lines.extend(["## Personal baseline used", ""])
    markers = baseline.get("markers", {})
    period = baseline.get("baseline_period", {})
    lines.append(
        f"Baseline period: {period.get('start')} to {period.get('end')} "
        f"(subject `{baseline.get('subject_id')}`)"
    )
    lines.append("")
    relevant_signals = sorted(
        {
            str(obs.get("signal_type"))
            for obs in raw_observations
            if obs.get("signal_type") in markers
        }
    )
    for signal in relevant_signals:
        stats = markers[signal]
        lines.append(
            f"- **{signal}:** median={stats.get('median')} {stats.get('unit', '')}, "
            f"std={stats.get('std')}, sample_count={stats.get('sample_count')}"
        )
    lines.append("")

    lines.extend(["## Derived markers", ""])
    for marker in derived_markers:
        lines.extend(
            [
                f"### {marker.get('marker_id')}",
                f"- **Derived node:** `{marker.get('derived_node')}`",
                f"- **Rule:** {marker.get('derivation_rule')}",
                f"- **Deviation score:** {marker.get('deviation_score')}",
                f"- **Confidence:** {marker.get('confidence')}",
                f"- **Supporting observations:** {', '.join(marker.get('supporting_observations', []))}",
                "",
            ]
        )

    lines.extend(
        [
            "Expected demo mappings:",
            "- sleep_duration 4.5h vs baseline 7.4h → `sleep_loss`",
            "- hrv_rmssd 28ms vs baseline 48ms → `reduced_hrv_relative_to_baseline`",
            "- eda 2.3 vs baseline 1.2 → `increased_eda`",
            "",
            "## Matched static graph nodes",
            "",
        ]
    )
    if matched_nodes:
        for node_id in matched_nodes:
            lines.append(f"- `{node_id}` ({node_id_to_label(node_id)})")
    else:
        lines.append("_No static graph nodes matched._")
    lines.append("")

    lines.extend(["## Inference input", ""])
    for obs in inference_observations:
        lines.extend(
            [
                f"### {obs.get('observation_id')}",
                f"- **Observed node:** `{obs.get('observed_node')}`",
                f"- **Quality score (confidence):** {obs.get('quality_score')}",
                f"- **Source:** {obs.get('source')}",
                f"- **Notes:** {obs.get('notes', '')}",
                "",
            ]
        )

    lines.extend(["## Warnings", ""])
    for warning in warnings:
        lines.append(f"- {warning}")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote personal evidence graph report to %s", path)


def build_personal_evidence_graph(
    raw_observations: list[dict[str, Any]],
    baseline: dict[str, Any],
    static_graph_path: Path,
    personal_graph_id: str = PERSONAL_GRAPH_ID,
    inference_result: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    nodes, _, graph = load_graph_nodes_and_edges(static_graph_path)
    static_node_ids = {str(n["node_id"]) for n in nodes}

    derived_markers = map_observations_to_derived_markers(raw_observations, baseline)
    node_errors, node_warnings = validate_derived_nodes_in_static_graph(
        derived_markers, static_node_ids
    )
    if node_errors:
        for error in node_errors:
            logger.error("Static node validation: %s", error)
        raise ValueError(
            f"{len(node_errors)} derived_node(s) missing from static graph: "
            + "; ".join(node_errors)
        )

    matched_static_nodes = build_matched_static_nodes(derived_markers, static_node_ids)
    inference_observations = derived_markers_to_inference_observations(
        derived_markers, raw_observations, static_node_ids
    )

    subject_ids = {str(o.get("subject_id", "")).strip() for o in raw_observations}
    subject_ids.add(str(baseline.get("subject_id", "")).strip())
    subject_ids.discard("")
    if len(subject_ids) > 1:
        node_warnings.append(
            f"Multiple subject_ids across inputs: {sorted(subject_ids)}"
        )
    subject_id = baseline.get("subject_id") or raw_observations[0].get("subject_id", "unknown")

    warnings = list(DEFAULT_WARNINGS) + node_warnings

    personal_graph = {
        "personal_graph_id": personal_graph_id,
        "subject_id": subject_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "raw_observations": raw_observations,
        "personal_baseline": baseline,
        "derived_markers": derived_markers,
        "matched_static_nodes": matched_static_nodes,
        "inference_input_observations": inference_observations,
        "inference_result": inference_result,
        "warnings": warnings,
        "static_graph_id": graph.get("graph_id", ""),
    }

    logger.info(
        "Built personal evidence graph: %d raw obs, %d derived markers, %d matched nodes",
        len(raw_observations),
        len(derived_markers),
        len(matched_static_nodes),
    )
    return personal_graph, inference_observations, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build personal evidence graph from raw observations and baseline."
    )
    parser.add_argument("--raw", type=Path, default=DEMO_RAW_OBSERVATIONS)
    parser.add_argument("--baseline", type=Path, default=DEMO_PERSONAL_BASELINE)
    parser.add_argument("--static-graph", type=Path, default=GRAPH_JSON)
    parser.add_argument("--output", type=Path, default=DEMO_PERSONAL_EVIDENCE_GRAPH)
    parser.add_argument(
        "--inference-input",
        type=Path,
        default=DEMO_INFERENCE_INPUT_FROM_PERSONAL_GRAPH,
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEMO_PERSONAL_EVIDENCE_GRAPH_REPORT,
    )
    parser.add_argument(
        "--inference-result",
        type=Path,
        default=None,
        help="Optional inference result JSON to embed in the personal evidence graph.",
    )
    parser.add_argument("--personal-graph-id", default=PERSONAL_GRAPH_ID)
    args = parser.parse_args()

    try:
        raw_observations = load_raw_observations(args.raw)
        baseline = load_personal_baseline(args.baseline)

        inference_result = None
        if args.inference_result and args.inference_result.is_file():
            inference_result = load_json_file(args.inference_result)
            logger.info("Embedding inference result from %s", args.inference_result)

        personal_graph, inference_observations, warnings = build_personal_evidence_graph(
            raw_observations,
            baseline,
            args.static_graph,
            personal_graph_id=args.personal_graph_id,
            inference_result=inference_result,
        )

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(personal_graph, indent=2) + "\n", encoding="utf-8")
        logger.info("Wrote personal evidence graph to %s", args.output)

        args.inference_input.parent.mkdir(parents=True, exist_ok=True)
        args.inference_input.write_text(
            json.dumps(inference_observations, indent=2) + "\n", encoding="utf-8"
        )
        logger.info("Wrote inference input observations to %s", args.inference_input)

        write_markdown_report(
            args.report,
            raw_observations=raw_observations,
            baseline=baseline,
            derived_markers=personal_graph["derived_markers"],
            matched_nodes=personal_graph["matched_static_nodes"],
            inference_observations=inference_observations,
            warnings=warnings,
        )

        print("=== THSI Personal Evidence Graph v0.1 — Build Summary ===")
        print(f"Raw observations: {len(raw_observations)}")
        print(f"Derived markers: {len(personal_graph['derived_markers'])}")
        print(f"Matched static nodes: {', '.join(personal_graph['matched_static_nodes'])}")
        print(f"Personal graph: {args.output}")
        print(f"Inference input: {args.inference_input}")
        print(f"Report: {args.report}")
        return 0

    except (ValueError, json.JSONDecodeError, FileNotFoundError) as exc:
        logger.error("Build failed: %s", exc)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
