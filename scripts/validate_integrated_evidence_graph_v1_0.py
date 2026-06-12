#!/usr/bin/env python3
"""Validate the THSI integrated evidence graph v1.0.

Checks (each logged, failures never hidden):
  1. graph / nodes / edges JSON files parse.
  2. every edge source/target exists as a node.
  3. no duplicate node ids; no duplicate edge ids.
  4. required hidden states present (or explicitly listed missing).
  5. required guardrails present (or explicitly listed missing).
  6. elevated_heart_rate_relative_to_baseline present.
  7. every hidden_state has >=1 incoming SUPPORTS_HIDDEN_STATE or PART_OF_CHAIN edge,
     unless its pipeline_status is partial or needs_review.
  8. every measured_parameter has source traceability (source_files or source_tree_ids
     or an outgoing SUPPORTED_BY_SOURCE / DERIVED_FROM edge).
  9. no edge uses diagnosis language as a final conclusion.
 10. stats consistent with the actual graph.

Writes:
  - outputs/validation/integrated_evidence_graph_validation_v1_0.json
  - outputs/validation/integrated_evidence_graph_validation_v1_0.md
"""

from __future__ import annotations

import json
import logging
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PKG_DIR = PROJECT_ROOT / "outputs" / "astronaut_data_mapping_v1_0"
VALIDATION_DIR = PROJECT_ROOT / "outputs" / "validation"

GRAPH_JSON = PKG_DIR / "integrated_evidence_graph_v1_0.json"
NODES_JSON = PKG_DIR / "integrated_evidence_graph_nodes_v1_0.json"
EDGES_JSON = PKG_DIR / "integrated_evidence_graph_edges_v1_0.json"
STATS_JSON = PKG_DIR / "integrated_evidence_graph_stats_v1_0.json"

REQUIRED_HIDDEN_STATES = [
    "low_recovery_state", "acute_sleep_loss", "sleep_fragmentation_recovery_failure",
    "circadian_misalignment", "orthostatic_intolerance", "hypovolemia_dehydration_hypothesis",
    "hyperventilation_hypocapnia_state", "environmental_CO2_performance_risk", "heat_strain",
    "infectious_or_inflammatory_load", "inflammatory_sickness_behavior", "postviral_immune_activation",
    "viral_reactivation_context", "metabolic_strain", "low_energy_availability",
    "catabolic_muscle_loss", "deconditioning", "PEM_objective_branch", "pain_sleep_fatigue_branch",
    "migraine_phenotype_branch", "iron_deficiency_oxygen_delivery_branch", "functional_B12_deficiency",
    "thyroid_dysfunction_context", "HPA_circadian_disruption", "medication_context_override",
    "bone_unloading_loss", "SANS_risk_branch", "renal_stone_risk_branch",
    "radiation_biological_effect_branch", "team_behavioral_risk", "microbiome_immune_context",
    "wearable_sleep_false_reassurance", "unknown_or_missing_data_state",
]

REQUIRED_GUARDRAILS = [
    "unknown_is_not_negative_evidence", "single_marker_never_equals_mechanism",
    "symptom_report_never_equals_mechanism", "context_override_before_mechanism",
    "medication_timing_first", "environmental_exposure_separate_from_physiologic_effect",
    "group_reference_separate_from_individual_baseline", "within_person_deviation_priority",
    "temporal_lag_required_for_causality", "objective_performance_separate_from_subjective_symptom",
    "imaging_abnormality_separate_from_functional_impairment", "microbiome_association_not_causality",
    "immune_marker_not_infection_without_symptoms", "radiation_dose_not_injury_without_biomarker_or_outcome",
    "SANS_not_subjective_vision_symptom", "PEM_not_normal_fatigue", "hydration_intake_not_hydration_status",
    "low_activity_not_fatigue", "low_VO2_not_mechanism", "normal_one_source_not_ruleout",
    "wearable_sleep_stage_not_PSG", "pain_limited_performance_not_muscle_weakness",
    "recommend_next_measurement_when_uncertain",
]

DIAGNOSIS_TOKENS = [
    "you have", "confirmed disease", "diagnosis confirmed", "definitive diagnosis",
    "diagnosed with", "you are diagnosed",
]

logger = logging.getLogger("validate_integrated_evidence_graph")


def configure_logging() -> None:
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S"))
    logger.addHandler(handler)


class Report:
    def __init__(self) -> None:
        self.checks: list[dict] = []

    def add(self, check_id: str, passed: bool, message: str, details=None) -> None:
        status = "PASS" if passed else "FAIL"
        self.checks.append(
            {"check": check_id, "status": status, "passed": passed,
             "message": message, "details": details or {}}
        )
        log = logger.info if passed else logger.error
        log("[%s] %s — %s", status, check_id, message)

    @property
    def all_passed(self) -> bool:
        return all(c["passed"] for c in self.checks)


def load_or_fail(path: Path, report: Report, check_id: str):
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        report.add(check_id, True, f"Parsed {path.name}")
        return data
    except FileNotFoundError:
        report.add(check_id, False, f"File not found: {path.name}")
    except json.JSONDecodeError as exc:
        report.add(check_id, False, f"JSON parse error in {path.name}: {exc}")
    return None


def main() -> int:
    configure_logging()
    logger.info("=== Validating THSI integrated evidence graph v1.0 ===")
    report = Report()

    graph = load_or_fail(GRAPH_JSON, report, "L1_parse_graph")
    nodes_doc = load_or_fail(NODES_JSON, report, "L1_parse_nodes")
    edges_doc = load_or_fail(EDGES_JSON, report, "L1_parse_edges")
    stats_doc = load_or_fail(STATS_JSON, report, "L1_parse_stats")

    if graph is None or nodes_doc is None or edges_doc is None:
        _write_outputs(report, {})
        logger.error("Cannot continue: core files failed to parse.")
        return 1

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    node_index = {n["id"]: n for n in nodes}

    # Check 2: edge endpoints exist.
    missing_endpoints = []
    for e in edges:
        if e["source"] not in node_index:
            missing_endpoints.append({"edge": e["id"], "missing": e["source"], "role": "source"})
        if e["target"] not in node_index:
            missing_endpoints.append({"edge": e["id"], "missing": e["target"], "role": "target"})
    report.add(
        "edge_endpoints_exist", not missing_endpoints,
        f"{len(missing_endpoints)} edge endpoints missing",
        {"examples": missing_endpoints[:20]},
    )

    # Check 3a: duplicate node ids.
    node_id_counts = Counter(n["id"] for n in nodes)
    dup_nodes = {k: v for k, v in node_id_counts.items() if v > 1}
    report.add("no_duplicate_node_ids", not dup_nodes,
               f"{len(dup_nodes)} duplicate node ids", {"duplicates": dup_nodes})

    # Check 3b: duplicate edge ids.
    edge_id_counts = Counter(e["id"] for e in edges)
    dup_edges = {k: v for k, v in edge_id_counts.items() if v > 1}
    report.add("no_duplicate_edge_ids", not dup_edges,
               f"{len(dup_edges)} duplicate edge ids", {"duplicates": dict(list(dup_edges.items())[:20])})

    # Check 4: required hidden states.
    missing_states = [s for s in REQUIRED_HIDDEN_STATES if s not in node_index]
    report.add("required_hidden_states_present", not missing_states,
               f"{len(REQUIRED_HIDDEN_STATES) - len(missing_states)}/{len(REQUIRED_HIDDEN_STATES)} required hidden states present",
               {"missing": missing_states})

    # Check 5: required guardrails.
    missing_guardrails = [g for g in REQUIRED_GUARDRAILS if g not in node_index]
    report.add("required_guardrails_present", not missing_guardrails,
               f"{len(REQUIRED_GUARDRAILS) - len(missing_guardrails)}/{len(REQUIRED_GUARDRAILS)} required guardrails present",
               {"missing": missing_guardrails})

    # Check 6: elevated HR node.
    report.add("elevated_hr_node_present",
               "elevated_heart_rate_relative_to_baseline" in node_index,
               "elevated_heart_rate_relative_to_baseline present")

    # Check 7: hidden_state support coverage.
    incoming_support = defaultdict(int)
    for e in edges:
        if e["type"] in ("SUPPORTS_HIDDEN_STATE", "PART_OF_CHAIN"):
            incoming_support[e["target"]] += 1
    unsupported = []
    for n in nodes:
        if n["type"] != "hidden_state":
            continue
        if n["pipeline_status"] in ("partial", "needs_review"):
            continue
        if incoming_support[n["id"]] == 0:
            unsupported.append(n["id"])
    report.add("hidden_state_support_coverage", not unsupported,
               f"{len(unsupported)} ready hidden states without incoming support edge",
               {"unsupported": unsupported})

    # Check 8: measured_parameter source traceability.
    has_source_edge = defaultdict(bool)
    for e in edges:
        if e["type"] in ("SUPPORTED_BY_SOURCE", "DERIVED_FROM", "MEASURES"):
            has_source_edge[e["source"]] = True
            has_source_edge[e["target"]] = True
    untraceable = []
    for n in nodes:
        if n["type"] != "measured_parameter":
            continue
        if n.get("source_files") or n.get("source_tree_ids") or has_source_edge[n["id"]]:
            continue
        untraceable.append(n["id"])
    report.add("measured_parameter_traceability", not untraceable,
               f"{len(untraceable)} measured parameters without source traceability",
               {"examples": untraceable[:20]})

    # Check 9: no diagnosis language in edge labels.
    diagnosis_edges = []
    for e in edges:
        text = f"{e.get('label','')} {e.get('metadata',{})}".lower()
        for token in DIAGNOSIS_TOKENS:
            if token in text:
                diagnosis_edges.append({"edge": e["id"], "token": token, "label": e.get("label")})
    report.add("no_diagnosis_language_in_edges", not diagnosis_edges,
               f"{len(diagnosis_edges)} edges contain diagnosis language",
               {"examples": diagnosis_edges[:20]})

    # Check 10: stats consistency.
    stats = graph.get("stats", {})
    actual_node_count = len(nodes)
    actual_edge_count = len(edges)
    actual_nodes_by_type = dict(sorted(Counter(n["type"] for n in nodes).items()))
    actual_edges_by_type = dict(sorted(Counter(e["type"] for e in edges).items()))
    inconsistencies = []
    if stats.get("node_count") != actual_node_count:
        inconsistencies.append(f"node_count {stats.get('node_count')} != {actual_node_count}")
    if stats.get("edge_count") != actual_edge_count:
        inconsistencies.append(f"edge_count {stats.get('edge_count')} != {actual_edge_count}")
    if stats.get("nodes_by_type") != actual_nodes_by_type:
        inconsistencies.append("nodes_by_type mismatch")
    if stats.get("edges_by_type") != actual_edges_by_type:
        inconsistencies.append("edges_by_type mismatch")
    for key in ("hidden_state_count", "guardrail_count", "measured_parameter_count", "source_tree_count"):
        type_key = key.replace("_count", "")
        if stats.get(key) != actual_nodes_by_type.get(type_key, 0):
            inconsistencies.append(f"{key} {stats.get(key)} != {actual_nodes_by_type.get(type_key, 0)}")
    # standalone stats file consistency
    if stats_doc is not None and stats_doc.get("stats", {}).get("node_count") != actual_node_count:
        inconsistencies.append("standalone stats file node_count mismatch")
    report.add("stats_consistent", not inconsistencies,
               f"{len(inconsistencies)} stats inconsistencies",
               {"inconsistencies": inconsistencies})

    # Cross-file consistency: standalone nodes/edges match embedded.
    standalone_nodes = nodes_doc.get("nodes", [])
    standalone_edges = edges_doc.get("edges", [])
    cross_ok = (len(standalone_nodes) == actual_node_count and len(standalone_edges) == actual_edge_count)
    report.add("standalone_files_match_graph", cross_ok,
               "standalone node/edge files match embedded graph",
               {"standalone_nodes": len(standalone_nodes), "standalone_edges": len(standalone_edges)})

    summary = {
        "node_count": actual_node_count,
        "edge_count": actual_edge_count,
        "nodes_by_type": actual_nodes_by_type,
        "edges_by_type": actual_edges_by_type,
        "hidden_state_count": actual_nodes_by_type.get("hidden_state", 0),
        "guardrail_count": actual_nodes_by_type.get("guardrail", 0),
        "checks_total": len(report.checks),
        "checks_passed": sum(1 for c in report.checks if c["passed"]),
        "checks_failed": sum(1 for c in report.checks if not c["passed"]),
        "overall_status": "PASS" if report.all_passed else "FAIL",
    }
    _write_outputs(report, summary)

    logger.info("=== Validation %s (%d/%d checks passed) ===",
                summary["overall_status"], summary["checks_passed"], summary["checks_total"])
    return 0 if report.all_passed else 1


def _write_outputs(report: Report, summary: dict) -> None:
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    doc = {
        "validator": "validate_integrated_evidence_graph_v1_0",
        "timestamp": timestamp,
        "overall_status": "PASS" if report.all_passed else "FAIL",
        "summary": summary,
        "checks": report.checks,
    }
    out_json = VALIDATION_DIR / "integrated_evidence_graph_validation_v1_0.json"
    out_json.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Integrated Evidence Graph v1.0 — Validation Report",
        "",
        f"- Validator: `validate_integrated_evidence_graph_v1_0`",
        f"- Timestamp: {timestamp}",
        f"- Overall status: **{doc['overall_status']}**",
        "",
    ]
    if summary:
        lines += [
            "## Summary",
            "",
            f"- Nodes: {summary.get('node_count')}",
            f"- Edges: {summary.get('edge_count')}",
            f"- Hidden states: {summary.get('hidden_state_count')}",
            f"- Guardrails: {summary.get('guardrail_count')}",
            f"- Checks passed: {summary.get('checks_passed')}/{summary.get('checks_total')}",
            "",
        ]
    lines += ["## Checks", "", "| Check | Status | Message |", "|---|---|---|"]
    for c in report.checks:
        lines.append(f"| {c['check']} | {c['status']} | {c['message']} |")
    lines.append("")
    lines.append("## Failing check details")
    lines.append("")
    any_fail = False
    for c in report.checks:
        if not c["passed"] and c["details"]:
            any_fail = True
            lines.append(f"### {c['check']}")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(c["details"], indent=2, ensure_ascii=False))
            lines.append("```")
            lines.append("")
    if not any_fail:
        lines.append("None.")
        lines.append("")
    out_md = VALIDATION_DIR / "integrated_evidence_graph_validation_v1_0.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", out_json.relative_to(PROJECT_ROOT))
    logger.info("Wrote %s", out_md.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    sys.exit(main())
