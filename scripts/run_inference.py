#!/usr/bin/env python3
"""THSI Inference Engine v0.1 — graph-based evidence-traceable inference from observations."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from _project_paths import (
    DEMO_INFERENCE_JSON,
    DEMO_INFERENCE_MD,
    DEMO_OBSERVATIONS,
    GRAPH_JSON,
    INFERENCE_ID,
)
from _static_graph import (
    aggregate_list_field,
    build_adjacency,
    collect_paths_bfs,
    infer_node_type,
    load_graph_nodes_and_edges,
    load_observations_json,
    node_has_forbidden_clinical_token,
    node_id_to_label,
    path_has_intermediate_bridge,
    query_graph,
)
from score_paths import hypothesis_score_from_paths, score_path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_WARNINGS = [
    "This output is not a medical diagnosis.",
    "All psychological outputs are cautious state hypotheses.",
    "Interpretation requires context and may change with additional observations.",
]


def validate_observations(
    observations: list[dict[str, Any]],
    node_ids: set[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    valid: list[dict[str, Any]] = []

    for obs in observations:
        observed_node = str(obs.get("observed_node", "")).strip()
        if observed_node not in node_ids:
            msg = f"observation {obs.get('observation_id')}: unknown observed_node '{observed_node}'"
            logger.error(msg)
            raise ValueError(msg)

        quality = obs.get("quality_score", 0)
        try:
            quality_value = float(quality)
        except (TypeError, ValueError):
            quality_value = 0.0

        if quality_value <= 0:
            warnings.append(
                f"Excluded observation {obs.get('observation_id')} "
                f"({observed_node}): quality_score <= 0"
            )
            logger.info(
                "Excluded observation %s: quality_score=%s",
                obs.get("observation_id"),
                quality,
            )
            continue

        valid.append(obs)

    return valid, warnings


def path_is_valid(
    node_path: list[str],
    edge_path: list[dict[str, Any]],
    node_types: dict[str, str],
) -> bool:
    for node_id in node_path:
        if node_has_forbidden_clinical_token(node_id):
            return False

    if not edge_path:
        return len(node_path) <= 1

    target = node_path[-1]
    target_type = node_types.get(target, infer_node_type(target))
    source = node_path[0]
    source_type = node_types.get(source, infer_node_type(source))

    if len(edge_path) == 1:
        if (
            source_type == "observable_marker"
            and target_type == "psychological_state_hypothesis"
        ):
            return False

    if target_type == "psychological_state_hypothesis":
        if not path_has_intermediate_bridge(node_path, node_types):
            return False

    return True


def collect_observation_paths(
    observation: dict[str, Any],
    adjacency: dict[str, list[dict[str, Any]]],
    node_types: dict[str, str],
    max_depth: int,
) -> list[dict[str, Any]]:
    start_node = str(observation["observed_node"]).strip()
    _, raw_paths = collect_paths_bfs(
        [start_node],
        adjacency,
        node_types,
        max_depth=max_depth,
    )

    valid_paths: list[dict[str, Any]] = []
    for entry in raw_paths:
        node_path = entry["node_path"]
        edge_path = entry["edge_path"]
        if not path_is_valid(node_path, edge_path, node_types):
            continue
        valid_paths.append(
            {
                "observation": observation,
                "node_path": node_path,
                "edge_path": edge_path,
                "target_node": entry["target_node"],
            }
        )
    return valid_paths


def format_scored_path(
    path_entry: dict[str, Any],
    node_labels: dict[str, str],
) -> dict[str, Any]:
    node_path = path_entry["node_path"]
    edge_path = path_entry["edge_path"]
    observation = path_entry["observation"]
    quality_score = float(observation.get("quality_score", 1.0))

    scoring = score_path(node_path, edge_path, quality_score=quality_score)
    context_requirements = aggregate_list_field(
        [edge.get("context_requirements") for edge in edge_path]
    )

    return {
        "path_score": scoring["path_score"],
        "observation_id": observation.get("observation_id"),
        "start_node": node_path[0] if node_path else "",
        "node_sequence": node_path,
        "node_labels": [node_labels.get(n, node_id_to_label(n)) for n in node_path],
        "edge_sequence": [edge.get("edge_id") for edge in edge_path],
        "source_ids": scoring["source_ids_used"],
        "relationship_types": [edge.get("relationship_type") for edge in edge_path],
        "limitations": scoring["limitations_used"],
        "context_requirements": context_requirements,
        "risk_of_overinterpretation": scoring["risk_of_overinterpretation"],
        "score_components": scoring["score_components"],
        "weakest_edge": scoring["weakest_edge"],
        "highest_risk_edge": scoring["highest_risk_edge"],
        "target_node": node_path[-1] if node_path else "",
    }


def build_interpretation(
    hypothesis_node: str,
    label: str,
    supporting_paths: list[dict[str, Any]],
    hypothesis_score: float,
) -> str:
    if not supporting_paths:
        return (
            f"No valid evidence paths currently support the cautious hypothesis "
            f"'{label}'. Additional observations and context are required."
        )

    best_path = max(supporting_paths, key=lambda p: p["path_score"])
    sequence = " → ".join(best_path["node_sequence"])
    start_obs = best_path.get("start_node", best_path["node_sequence"][0])
    score_text = f"{hypothesis_score:.2f}"

    return (
        f"Observed `{start_obs}` (among other inputs) supports literature-backed "
        f"pathways that may be compatible with a cautious '{label}' hypothesis "
        f"(preliminary score {score_text}). "
        f"Primary supporting path: {sequence}. "
        f"This reflects evidence-linked mechanism traversal, not a clinical "
        f"conclusion; context is required and alternative explanations remain possible."
    )


def build_hypotheses(
    scored_paths: list[dict[str, Any]],
    node_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    by_hypothesis: dict[str, list[dict[str, Any]]] = {}
    for path in scored_paths:
        target = path["target_node"]
        target_type = node_by_id.get(target, {}).get(
            "node_type", infer_node_type(target)
        )
        if target_type != "psychological_state_hypothesis":
            continue
        by_hypothesis.setdefault(target, []).append(path)

    hypotheses: list[dict[str, Any]] = []
    for hypothesis_node, paths in by_hypothesis.items():
        path_scores = [p["path_score"] for p in paths]
        hyp_score = hypothesis_score_from_paths(path_scores)
        label = node_by_id.get(hypothesis_node, {}).get(
            "label", node_id_to_label(hypothesis_node)
        )
        all_limitations = aggregate_list_field([p.get("limitations") for p in paths])
        supporting = sorted(paths, key=lambda p: p["path_score"], reverse=True)

        path_payloads = [
            {
                "path_score": p["path_score"],
                "node_sequence": p["node_sequence"],
                "edge_sequence": p["edge_sequence"],
                "source_ids": p["source_ids"],
                "relationship_types": p["relationship_types"],
                "limitations": p["limitations"],
                "context_requirements": p["context_requirements"],
                "risk_of_overinterpretation": p["risk_of_overinterpretation"],
                "score_components": p["score_components"],
            }
            for p in supporting
        ]

        hypotheses.append(
            {
                "hypothesis_node": hypothesis_node,
                "label": label,
                "hypothesis_score": hyp_score,
                "interpretation": build_interpretation(
                    hypothesis_node, label, supporting, hyp_score
                ),
                "supporting_paths": path_payloads,
                "limitations": all_limitations,
                "not_diagnostic_warning": True,
            }
        )

    hypotheses.sort(key=lambda h: h["hypothesis_score"], reverse=True)
    return hypotheses


def build_reachable_summary(
    reachable_nodes: list[str],
    node_types: dict[str, str],
) -> dict[str, list[str]]:
    def nodes_of_type(type_name: str) -> list[str]:
        return sorted(
            node_id
            for node_id in reachable_nodes
            if node_types.get(node_id, infer_node_type(node_id)) == type_name
        )

    return {
        "physiological_mechanisms": nodes_of_type("physiological_mechanism"),
        "biochemical_markers": nodes_of_type("biochemical_marker"),
        "neurobiological_affective_bridge_nodes": nodes_of_type(
            "neurobiological_affective_bridge"
        ),
        "risk_states": nodes_of_type("risk_state"),
        "psychological_state_hypotheses": nodes_of_type(
            "psychological_state_hypothesis"
        ),
    }


def write_markdown_report(
    out_path: Path,
    result: dict[str, Any],
    node_labels: dict[str, str],
) -> None:
    lines = [
        "# THSI Inference Report v0.1",
        "",
        f"**Inference ID:** {result['inference_id']}",
        f"**Subject:** {result['subject_id']}",
        f"**Created:** {result['created_at']}",
        "",
        "## Input observations",
        "",
    ]

    for obs in result["input_observations"]:
        node_label = node_labels.get(
            obs["observed_node"], node_id_to_label(obs["observed_node"])
        )
        lines.extend(
            [
                f"### {obs['observation_id']}",
                f"- **Node:** `{obs['observed_node']}` ({node_label})",
                f"- **Value:** {json.dumps(obs['value'])}",
                f"- **Source:** {obs['source']}",
                f"- **Quality score:** {obs['quality_score']}",
                f"- **Notes:** {obs.get('notes', '')}",
                "",
            ]
        )

    lines.extend(["## Supported mechanisms", ""])
    mechanism_notes = {
        "sleep_loss": (
            "Observed sleep loss may support pathways involving emotion regulation "
            "impairment and reduced positive affect, and may be compatible with "
            "recovery-related mechanism chains when combined with other signals."
        ),
        "increased_eda": (
            "Observed increased EDA may support sympathetic arousal and acute arousal "
            "mechanism pathways; EDA is not emotion-specific and requires context."
        ),
        "reduced_hrv_relative_to_baseline": (
            "Observed reduced HRV relative to baseline may support autonomic "
            "regulation shift and downstream recovery-deficit mechanism pathways; "
            "interpretation requires baseline-sensitive context."
        ),
    }
    matched = set(result.get("matched_observed_nodes", []))
    for node_id, note in mechanism_notes.items():
        if node_id in matched:
            lines.append(f"- **{node_id_to_label(node_id)}:** {note}")
    summary = result.get("reachable_summary", {})
    for mechanism in summary.get("physiological_mechanisms", []):
        if mechanism not in matched:
            lines.append(
                f"- **{node_labels.get(mechanism, node_id_to_label(mechanism))}:** "
                f"Reachable via evidence paths from observed inputs."
            )
    lines.append("")

    lines.extend(["## Cautious state hypotheses", ""])
    hypotheses = result.get("hypotheses", [])
    if not hypotheses:
        lines.append(
            "_No psychological state hypotheses were supported by valid evidence paths._"
        )
        lines.append("")
    else:
        for hyp in hypotheses:
            lines.extend(
                [
                    f"### {hyp['label']}",
                    f"- **Preliminary score:** {hyp['hypothesis_score']:.3f}",
                    f"- **Interpretation:** {hyp['interpretation']}",
                    f"- **Supporting paths:** {len(hyp['supporting_paths'])}",
                ]
            )
            for path in hyp["supporting_paths"][:3]:
                seq = " → ".join(path["node_sequence"])
                lines.append(
                    f"  - Path (score {path['path_score']:.3f}): {seq}"
                )
                lines.append(
                    f"    Sources: {', '.join(path['source_ids'])}"
                )
            if hyp.get("limitations"):
                lines.append("- **Limitations:**")
                for lim in hyp["limitations"][:6]:
                    lines.append(f"  - {lim}")
            lines.append(
                "- **Warning:** This is a cautious state hypothesis, not a clinical "
                "conclusion."
            )
            lines.append("")

    lines.extend(["## Evidence paths", ""])
    for index, path in enumerate(result.get("all_evidence_paths", [])[:15], start=1):
        seq_lines = path["node_sequence"]
        formatted = "\n→ ".join(seq_lines)
        lines.extend(
            [
                f"### Path {index} (score {path['path_score']:.3f})",
                formatted,
                f"- Sources: {', '.join(path['source_ids'])}",
                "",
            ]
        )
    if len(result.get("all_evidence_paths", [])) > 15:
        omitted = len(result["all_evidence_paths"]) - 15
        lines.append(f"_({omitted} additional paths omitted)_")
        lines.append("")

    lines.extend(["## Limitations", ""])
    all_limitations: list[str] = []
    seen: set[str] = set()
    for path in result.get("all_evidence_paths", []):
        for lim in path.get("limitations", []):
            if lim not in seen:
                seen.add(lim)
                all_limitations.append(lim)
    highlight = [
        "EDA is not emotion-specific",
        "HRV is not diagnosis-specific",
        "sleep loss does not identify a specific disorder",
        "fatigue has many causes",
        "context is required",
    ]
    for item in highlight:
        lines.append(f"- {item}")
    for lim in all_limitations[:10]:
        if lim not in highlight:
            lines.append(f"- {lim}")
    lines.append("")

    lines.extend(
        [
            "## Warning",
            "",
            "This is not a medical diagnosis. All psychological outputs are cautious "
            "state hypotheses that require context, may change with additional "
            "observations, and must not be read as proof of any disorder or clinical "
            "condition.",
            "",
        ]
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote inference markdown report to %s", out_path)


def run_inference(
    graph_path: Path,
    observations_path: Path,
    max_depth: int = 4,
    inference_id: str = INFERENCE_ID,
) -> dict[str, Any]:
    nodes, edges, graph = load_graph_nodes_and_edges(graph_path)
    observations = load_observations_json(observations_path)
    node_by_id = {n["node_id"]: n for n in nodes}
    node_ids = set(node_by_id)
    node_types = {n["node_id"]: n["node_type"] for n in nodes}
    node_labels = {n["node_id"]: n.get("label", node_id_to_label(n["node_id"])) for n in nodes}
    adjacency = build_adjacency(edges)

    valid_observations, obs_warnings = validate_observations(observations, node_ids)
    if not valid_observations:
        raise ValueError("No observations with quality_score > 0 remain after filtering")

    subject_ids = {str(o.get("subject_id", "")).strip() for o in valid_observations}
    if len(subject_ids) > 1:
        logger.warning(
            "Multiple subject_ids in observations: %s; using first",
            sorted(subject_ids),
        )
    subject_id = valid_observations[0].get("subject_id", "unknown")

    matched_observed_nodes = sorted(
        {str(o["observed_node"]).strip() for o in valid_observations}
    )

    query_result = query_graph(matched_observed_nodes, edges, nodes, max_depth=max_depth)
    reachable_summary = build_reachable_summary(
        query_result["reachable_nodes"], node_types
    )

    all_path_entries: list[dict[str, Any]] = []
    for observation in valid_observations:
        all_path_entries.extend(
            collect_observation_paths(observation, adjacency, node_types, max_depth)
        )

    scored_paths = [format_scored_path(entry, node_labels) for entry in all_path_entries]
    scored_paths.sort(key=lambda p: p["path_score"], reverse=True)

    hypotheses = build_hypotheses(scored_paths, node_by_id)

    all_evidence_paths = [
        {
            "path_score": p["path_score"],
            "observation_id": p.get("observation_id"),
            "node_sequence": p["node_sequence"],
            "edge_sequence": p["edge_sequence"],
            "source_ids": p["source_ids"],
            "relationship_types": p["relationship_types"],
            "limitations": p["limitations"],
            "context_requirements": p["context_requirements"],
            "risk_of_overinterpretation": p["risk_of_overinterpretation"],
            "score_components": p["score_components"],
        }
        for p in scored_paths
    ]

    warnings = list(DEFAULT_WARNINGS) + obs_warnings

    result = {
        "inference_id": inference_id,
        "graph_id": graph.get("graph_id", ""),
        "subject_id": subject_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_observations": valid_observations,
        "matched_observed_nodes": matched_observed_nodes,
        "reachable_summary": reachable_summary,
        "hypotheses": hypotheses,
        "all_evidence_paths": all_evidence_paths,
        "warnings": warnings,
    }

    logger.info(
        "Inference complete: %d observations, %d paths, %d hypotheses",
        len(valid_observations),
        len(all_evidence_paths),
        len(hypotheses),
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run THSI graph-based inference from personal observations."
    )
    parser.add_argument("--graph", type=Path, default=GRAPH_JSON)
    parser.add_argument("--observations", type=Path, default=DEMO_OBSERVATIONS)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--output-json", type=Path, default=DEMO_INFERENCE_JSON)
    parser.add_argument("--output-md", type=Path, default=DEMO_INFERENCE_MD)
    parser.add_argument("--inference-id", default=INFERENCE_ID)
    args = parser.parse_args()

    try:
        result = run_inference(
            args.graph,
            args.observations,
            max_depth=args.max_depth,
            inference_id=args.inference_id,
        )

        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        logger.info("Wrote inference JSON to %s", args.output_json)

        nodes, _, _ = load_graph_nodes_and_edges(args.graph)
        node_labels = {
            n["node_id"]: n.get("label", node_id_to_label(n["node_id"])) for n in nodes
        }
        write_markdown_report(args.output_md, result, node_labels)

        print("=== THSI Inference Engine v0.1 — Run Summary ===")
        print(f"Observations loaded: {len(result['input_observations'])}")
        print(f"Evidence paths found: {len(result['all_evidence_paths'])}")
        print(f"Hypotheses returned: {len(result['hypotheses'])}")
        for hyp in result["hypotheses"]:
            print(
                f"  - {hyp['hypothesis_node']}: "
                f"score={hyp['hypothesis_score']:.4f}"
            )
        print(f"JSON output: {args.output_json}")
        print(f"Markdown report: {args.output_md}")
        return 0

    except (ValueError, json.JSONDecodeError, FileNotFoundError) as exc:
        logger.error("Inference failed: %s", exc)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
