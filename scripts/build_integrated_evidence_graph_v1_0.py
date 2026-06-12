#!/usr/bin/env python3
"""Build the THSI / BodyState Mapper integrated evidence graph v1.0.

Scientific name: Traceable Human State Inference Under Partial Biological Observability.

This script assembles a single integrated, traceable evidence graph from existing
project artifacts ONLY. It does not invent evidence, does not produce diagnoses, and
preserves source traceability for every node and edge.

Inputs (all must already exist in the repository):
  - data/static_nodes_v0_1.json
  - data/static_scientific_evidence_graph_v0_1.json
  - outputs/astronaut_data_mapping_v1_0/measured_parameter_registry_v1_0.json
  - outputs/astronaut_data_mapping_v1_0/hidden_state_candidates_v1_0.json
  - outputs/astronaut_data_mapping_v1_0/inference_chains_v1_0.json
  - outputs/astronaut_data_mapping_v1_0/guardrails_v1_0.json
  - outputs/astronaut_data_mapping_v1_0/required_measurements_v1_0.json
  - outputs/astronaut_data_mapping_v1_0/cross_modal_links_v1_0.json
  - outputs/astronaut_data_mapping_v1_0/all_to_all_matrix_v1_0.json
  - outputs/astronaut_data_mapping_v1_0/result_variation_trees_v1_0.json
  - outputs/astronaut_data_mapping_v1_0/source_file_inventory_v1_0.json
  - outputs/astronaut_data_mapping_v1_0/astronaut_data_sources_v1_0.json
  - outputs/astronaut_data_mapping_v1_0/data_intake_contract_v1_0.json

Outputs:
  - outputs/astronaut_data_mapping_v1_0/integrated_evidence_graph_v1_0.json
  - outputs/astronaut_data_mapping_v1_0/integrated_evidence_graph_nodes_v1_0.json
  - outputs/astronaut_data_mapping_v1_0/integrated_evidence_graph_edges_v1_0.json
  - outputs/astronaut_data_mapping_v1_0/integrated_evidence_graph_stats_v1_0.json
"""

from __future__ import annotations

import json
import logging
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PKG_DIR = PROJECT_ROOT / "outputs" / "astronaut_data_mapping_v1_0"

GRAPH_ID = "thsi_integrated_evidence_graph_v1_0"
GRAPH_VERSION = "1.0"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("build_integrated_evidence_graph")


def configure_logging() -> None:
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S")
    )
    logger.addHandler(handler)


# ---------------------------------------------------------------------------
# Controlled vocabularies (must match task specification)
# ---------------------------------------------------------------------------
NODE_TYPES = {
    "source_file",
    "source_tree",
    "measured_parameter",
    "result_variation",
    "context",
    "hidden_state",
    "inference_chain",
    "guardrail",
    "required_measurement",
    "evidence_source",
    "data_quality_flag",
    "observation_input_type",
    "response_type",
}

EDGE_TYPES = {
    "CONTAINS",
    "MEASURES",
    "HAS_VARIATION",
    "REQUIRES_CONTEXT",
    "SUPPORTS_HIDDEN_STATE",
    "CONTRADICTS_OR_REDUCES_CONFIDENCE",
    "CONSTRAINED_BY_GUARDRAIL",
    "RECOMMENDS_MEASUREMENT",
    "PART_OF_CHAIN",
    "SUPPORTED_BY_SOURCE",
    "DERIVED_FROM",
    "ALIAS_OF",
    "CONTEXT_OVERRIDES",
    "NEEDS_REVIEW",
    "CAN_ACCEPT_INPUT",
    "CAN_OUTPUT_RESPONSE",
}

REQUIRED_HIDDEN_STATES = [
    "low_recovery_state",
    "acute_sleep_loss",
    "sleep_fragmentation_recovery_failure",
    "circadian_misalignment",
    "orthostatic_intolerance",
    "hypovolemia_dehydration_hypothesis",
    "hyperventilation_hypocapnia_state",
    "environmental_CO2_performance_risk",
    "heat_strain",
    "infectious_or_inflammatory_load",
    "inflammatory_sickness_behavior",
    "postviral_immune_activation",
    "viral_reactivation_context",
    "metabolic_strain",
    "low_energy_availability",
    "catabolic_muscle_loss",
    "deconditioning",
    "PEM_objective_branch",
    "pain_sleep_fatigue_branch",
    "migraine_phenotype_branch",
    "iron_deficiency_oxygen_delivery_branch",
    "functional_B12_deficiency",
    "thyroid_dysfunction_context",
    "HPA_circadian_disruption",
    "medication_context_override",
    "bone_unloading_loss",
    "SANS_risk_branch",
    "renal_stone_risk_branch",
    "radiation_biological_effect_branch",
    "team_behavioral_risk",
    "microbiome_immune_context",
    "wearable_sleep_false_reassurance",
    "unknown_or_missing_data_state",
]

REQUIRED_GUARDRAILS = [
    "unknown_is_not_negative_evidence",
    "single_marker_never_equals_mechanism",
    "symptom_report_never_equals_mechanism",
    "context_override_before_mechanism",
    "medication_timing_first",
    "environmental_exposure_separate_from_physiologic_effect",
    "group_reference_separate_from_individual_baseline",
    "within_person_deviation_priority",
    "temporal_lag_required_for_causality",
    "objective_performance_separate_from_subjective_symptom",
    "imaging_abnormality_separate_from_functional_impairment",
    "microbiome_association_not_causality",
    "immune_marker_not_infection_without_symptoms",
    "radiation_dose_not_injury_without_biomarker_or_outcome",
    "SANS_not_subjective_vision_symptom",
    "PEM_not_normal_fatigue",
    "hydration_intake_not_hydration_status",
    "low_activity_not_fatigue",
    "low_VO2_not_mechanism",
    "normal_one_source_not_ruleout",
    "wearable_sleep_stage_not_PSG",
    "pain_limited_performance_not_muscle_weakness",
    "recommend_next_measurement_when_uncertain",
]

# Universal guardrails that the intake contract requires on EVERY output.
UNIVERSAL_GUARDRAILS = [
    "unknown_is_not_negative_evidence",
    "single_marker_never_equals_mechanism",
    "symptom_report_never_equals_mechanism",
    "context_override_before_mechanism",
    "medication_timing_first",
]

# Definitional guardrail -> hidden_state bindings. These are not invented evidence;
# they are the named guardrail that, by definition, constrains interpretation of a
# given hidden state. Only bindings whose endpoints both exist are emitted.
GUARDRAIL_STATE_BINDINGS = {
    "PEM_not_normal_fatigue": ["PEM_objective_branch"],
    "SANS_not_subjective_vision_symptom": ["SANS_risk_branch"],
    "hydration_intake_not_hydration_status": ["hypovolemia_dehydration_hypothesis"],
    "low_VO2_not_mechanism": ["deconditioning"],
    "low_activity_not_fatigue": ["low_recovery_state", "deconditioning"],
    "wearable_sleep_stage_not_PSG": [
        "wearable_sleep_false_reassurance",
        "sleep_fragmentation_recovery_failure",
        "acute_sleep_loss",
    ],
    "radiation_dose_not_injury_without_biomarker_or_outcome": [
        "radiation_biological_effect_branch"
    ],
    "immune_marker_not_infection_without_symptoms": [
        "infectious_or_inflammatory_load",
        "inflammatory_sickness_behavior",
    ],
    "microbiome_association_not_causality": ["microbiome_immune_context"],
    "imaging_abnormality_separate_from_functional_impairment": [
        "SANS_risk_branch",
        "bone_unloading_loss",
        "deconditioning",
    ],
    "environmental_exposure_separate_from_physiologic_effect": [
        "environmental_CO2_performance_risk",
        "heat_strain",
    ],
    "pain_limited_performance_not_muscle_weakness": [
        "pain_sleep_fatigue_branch",
        "catabolic_muscle_loss",
    ],
    "objective_performance_separate_from_subjective_symptom": [
        "PEM_objective_branch",
    ],
    "within_person_deviation_priority": ["low_recovery_state"],
    "normal_one_source_not_ruleout": ["unknown_or_missing_data_state"],
    "recommend_next_measurement_when_uncertain": ["unknown_or_missing_data_state"],
}

# Forbidden diagnosis-language tokens for final-conclusion edge labels.
DIAGNOSIS_TOKENS = [
    "you have",
    "confirmed disease",
    "diagnosis confirmed",
    "definitive diagnosis",
    "diagnosed with",
]

CONFIDENCE_VALUES = {"high", "moderate", "low", "unknown"}
NODE_CONFIDENCE_VALUES = {"high", "moderate", "low", "insufficient", "unknown"}
EVIDENCE_STRENGTH_VALUES = {"high", "moderate", "low", "mixed", "unknown"}
PIPELINE_STATUS_VALUES = {"ready", "partial", "needs_review"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_json(path: Path) -> object:
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    logger.info("Loaded %s (%d bytes)", path.relative_to(PROJECT_ROOT), path.stat().st_size)
    return data


def slug(text: str) -> str:
    """Normalize free text to a stable id fragment."""
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unknown"


def norm_id(value: str) -> str:
    """Normalize an already-snake_case id for dedupe (case-insensitive)."""
    return (value or "").strip()


def normalize_confidence(value, default="unknown") -> str:
    v = (str(value or "")).strip().lower()
    if v in CONFIDENCE_VALUES:
        return v
    if v in ("insufficient",):
        return "low"
    return default


def normalize_node_confidence(value, default="unknown") -> str:
    v = (str(value or "")).strip().lower()
    if v in NODE_CONFIDENCE_VALUES:
        return v
    return default


def normalize_evidence_strength(value, default="unknown") -> str:
    v = (str(value or "")).strip().lower()
    if v in EVIDENCE_STRENGTH_VALUES:
        return v
    return default


def normalize_pipeline_status(value, default="needs_review") -> str:
    v = (str(value or "")).strip().lower()
    if v in PIPELINE_STATUS_VALUES:
        return v
    return default


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------
class GraphBuilder:
    def __init__(self) -> None:
        self.nodes: dict[str, dict] = {}
        self.edges: dict[str, dict] = {}
        self._node_type_counts: Counter = Counter()
        self._edge_type_counts: Counter = Counter()
        self._dropped_edges = 0

    # -- node/edge primitives -------------------------------------------------
    def add_node(
        self,
        node_id: str,
        label: str,
        node_type: str,
        domain: str = "",
        description: str = "",
        source_files=None,
        source_tree_ids=None,
        evidence_strength: str = "unknown",
        confidence: str = "unknown",
        pipeline_status: str = "needs_review",
        metadata=None,
    ) -> str:
        if node_type not in NODE_TYPES:
            raise ValueError(f"Illegal node type: {node_type} for {node_id}")
        node_id = norm_id(node_id)
        if not node_id:
            raise ValueError("Empty node id")
        if node_id in self.nodes:
            # Dedupe: merge source traceability and keep richest description.
            existing = self.nodes[node_id]
            if existing["type"] != node_type:
                raise ValueError(
                    f"Node id collision across types: {node_id} "
                    f"({existing['type']} vs {node_type})"
                )
            existing["source_files"] = sorted(
                set(existing["source_files"]) | set(source_files or [])
            )
            existing["source_tree_ids"] = sorted(
                set(existing["source_tree_ids"]) | set(source_tree_ids or [])
            )
            if len(description) > len(existing.get("description", "")):
                existing["description"] = description
            return node_id

        self.nodes[node_id] = {
            "id": node_id,
            "label": label or node_id,
            "type": node_type,
            "domain": domain or "",
            "description": description or "",
            "source_files": sorted(set(source_files or [])),
            "source_tree_ids": sorted(set(source_tree_ids or [])),
            "evidence_strength": normalize_evidence_strength(evidence_strength),
            "confidence": normalize_node_confidence(confidence),
            "pipeline_status": normalize_pipeline_status(pipeline_status),
            "metadata": metadata or {},
        }
        self._node_type_counts[node_type] += 1
        return node_id

    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: str,
        label: str = "",
        confidence: str = "unknown",
        source_files=None,
        source_tree_ids=None,
        chain_ids=None,
        guardrails=None,
        metadata=None,
    ) -> str | None:
        if edge_type not in EDGE_TYPES:
            raise ValueError(f"Illegal edge type: {edge_type}")
        source = norm_id(source)
        target = norm_id(target)
        if source not in self.nodes or target not in self.nodes:
            self._dropped_edges += 1
            logger.debug(
                "Dropping edge %s -%s-> %s (missing endpoint)", source, edge_type, target
            )
            return None
        edge_id = f"{source}__{edge_type}__{target}"
        if edge_id in self.edges:
            existing = self.edges[edge_id]
            existing["source_files"] = sorted(
                set(existing["source_files"]) | set(source_files or [])
            )
            existing["source_tree_ids"] = sorted(
                set(existing["source_tree_ids"]) | set(source_tree_ids or [])
            )
            existing["chain_ids"] = sorted(set(existing["chain_ids"]) | set(chain_ids or []))
            existing["guardrails"] = sorted(set(existing["guardrails"]) | set(guardrails or []))
            return edge_id

        label = label or edge_type.replace("_", " ").title()
        lowered = label.lower()
        for token in DIAGNOSIS_TOKENS:
            if token in lowered:
                raise ValueError(f"Edge label contains diagnosis language: {label!r}")
        self.edges[edge_id] = {
            "id": edge_id,
            "source": source,
            "target": target,
            "type": edge_type,
            "label": label,
            "confidence": normalize_confidence(confidence),
            "source_files": sorted(set(source_files or [])),
            "source_tree_ids": sorted(set(source_tree_ids or [])),
            "chain_ids": sorted(set(chain_ids or [])),
            "guardrails": sorted(set(guardrails or [])),
            "metadata": metadata or {},
        }
        self._edge_type_counts[edge_type] += 1
        return edge_id

    def has_node(self, node_id: str) -> bool:
        return norm_id(node_id) in self.nodes


# ---------------------------------------------------------------------------
# Build stages
# ---------------------------------------------------------------------------
def build_source_nodes(gb: GraphBuilder, data_sources, inventory) -> None:
    """source_file + source_tree nodes from astronaut data sources and inventory."""
    inv_by_name = {f["filename"]: f for f in inventory.get("files", [])}
    tree_count = 0
    for src in data_sources.get("sources", []):
        filename = src["filename"]
        tree_id = src.get("source_id") or slug(filename)
        rel = src.get("relative_path", filename)
        role = src.get("inferred_role", "")
        inv = inv_by_name.get(filename, {})
        file_node = f"file::{filename}"
        gb.add_node(
            file_node,
            label=filename,
            node_type="source_file",
            domain=role,
            description=f"Astronaut pipeline source file. Role={role}. Path={rel}.",
            source_files=[filename],
            source_tree_ids=[tree_id],
            evidence_strength="unknown",
            confidence="unknown",
            pipeline_status="ready" if inv.get("json_parse_status") == "valid" else "needs_review",
            metadata={
                "relative_path": rel,
                "inferred_role": role,
                "pipeline_use_priority": src.get("pipeline_use_priority"),
                "json_parse_status": inv.get("json_parse_status"),
                "file_size_bytes": inv.get("file_size_bytes"),
            },
        )
        tree_node = f"tree::{tree_id}"
        gb.add_node(
            tree_node,
            label=tree_id,
            node_type="source_tree",
            domain=role,
            description=f"Canonical source tree derived from {filename}.",
            source_files=[filename],
            source_tree_ids=[tree_id],
            pipeline_status="ready" if inv.get("json_parse_status") == "valid" else "needs_review",
            metadata={"inferred_role": role, "filename": filename},
        )
        tree_count += 1
        gb.add_edge(
            file_node,
            tree_node,
            "CONTAINS",
            label="source file contains source tree",
            confidence="high",
            source_files=[filename],
            source_tree_ids=[tree_id],
        )
        # Preserve alias provenance (inventory alias_of).
        alias_target = inv.get("alias_of")
        if alias_target and alias_target != filename:
            gb.add_node(
                f"file::{alias_target}",
                label=alias_target,
                node_type="source_file",
                description=f"Canonical source file for alias {filename}.",
                source_files=[alias_target],
                pipeline_status="ready",
            )
            gb.add_edge(
                file_node,
                f"file::{alias_target}",
                "ALIAS_OF",
                label="source file alias of canonical file",
                confidence="high",
            )
    logger.info("Built %d source_tree nodes from astronaut data sources", tree_count)


def ensure_tree_and_file(gb: GraphBuilder, tree_id: str, filename: str) -> tuple[str, str]:
    """Ensure a source_tree and source_file node exist for traceability."""
    file_node = ""
    if filename:
        file_node = f"file::{filename}"
        if not gb.has_node(file_node):
            gb.add_node(
                file_node,
                label=filename,
                node_type="source_file",
                description=f"Source file referenced by package data: {filename}.",
                source_files=[filename],
                source_tree_ids=[tree_id] if tree_id else None,
                pipeline_status="ready",
            )
    tree_node = ""
    if tree_id:
        tree_node = f"tree::{tree_id}"
        if not gb.has_node(tree_node):
            gb.add_node(
                tree_node,
                label=tree_id,
                node_type="source_tree",
                description=f"Source tree referenced by package data: {tree_id}.",
                source_files=[filename] if filename else None,
                source_tree_ids=[tree_id],
                pipeline_status="ready",
            )
        if file_node:
            gb.add_edge(
                file_node,
                tree_node,
                "CONTAINS",
                label="source file contains source tree",
                confidence="high",
                source_files=[filename] if filename else None,
                source_tree_ids=[tree_id],
            )
    return tree_node, file_node


def context_node(gb: GraphBuilder, text: str) -> str:
    cid = f"context::{slug(text)}"
    if not gb.has_node(cid):
        gb.add_node(
            cid,
            label=text.strip(),
            node_type="context",
            description=f"Contextual factor required for correct interpretation: {text.strip()}.",
            evidence_strength="unknown",
            confidence="unknown",
            pipeline_status="ready",
        )
    return cid


def measurement_node(gb: GraphBuilder, text: str, source_files) -> str:
    mid = f"measurement::{slug(text)}"
    if not gb.has_node(mid):
        gb.add_node(
            mid,
            label=text.strip(),
            node_type="required_measurement",
            description=f"Recommended next-best measurement to reduce uncertainty: {text.strip()}.",
            source_files=source_files,
            pipeline_status="ready",
        )
    return mid


def build_measured_parameters(gb: GraphBuilder, registry, hidden_state_ids) -> None:
    params = registry.get("parameters", [])
    param_ids = set()
    var_count = 0
    for p in params:
        pid = norm_id(p["parameter_id"])
        if pid in hidden_state_ids:
            # Avoid cross-type id collision with a hidden_state node.
            pid_node = f"param::{pid}"
        else:
            pid_node = pid
        param_ids.add(pid_node)
        files = p.get("source_files", [])
        trees = p.get("source_tree_ids", [])
        domain = (p.get("domains") or [""])[0] if p.get("domains") else ""
        gb.add_node(
            pid_node,
            label=p.get("display_name") or pid,
            node_type="measured_parameter",
            domain=domain,
            description=(p.get("standalone_interpretation") or [""])[0]
            if p.get("standalone_interpretation")
            else f"Measured parameter {p.get('display_name') or pid}.",
            source_files=files,
            source_tree_ids=trees,
            evidence_strength=normalize_evidence_strength(p.get("evidence_strength")),
            confidence="unknown",
            pipeline_status=normalize_pipeline_status(p.get("pipeline_status")),
            metadata={
                "aliases": p.get("aliases", []),
                "measurement_types": p.get("measurement_types", []),
                "sample_or_sensor": p.get("sample_or_sensor", []),
                "units_if_known": p.get("units_if_known", []),
                "requires_context": p.get("requires_context"),
                "human_evidence": p.get("human_evidence"),
                "astronaut_specific_evidence": p.get("astronaut_specific_evidence"),
                "data_quality_notes": p.get("data_quality_notes", []),
                "do_not_infer": p.get("do_not_infer", []),
            },
        )
        # Source traceability edges.
        for tree_id in trees:
            tree_node, _ = ensure_tree_and_file(gb, tree_id, files[0] if files else "")
            if tree_node:
                gb.add_edge(
                    tree_node,
                    pid_node,
                    "MEASURES",
                    label="source tree measures parameter",
                    confidence="high",
                    source_tree_ids=[tree_id],
                )
                gb.add_edge(
                    pid_node,
                    tree_node,
                    "DERIVED_FROM",
                    label="parameter derived from source tree",
                    confidence="high",
                    source_tree_ids=[tree_id],
                )
        for fname in files:
            ensure_tree_and_file(gb, trees[0] if trees else "", fname)
            gb.add_edge(
                pid_node,
                f"file::{fname}",
                "SUPPORTED_BY_SOURCE",
                label="parameter supported by source file",
                confidence="high",
                source_files=[fname],
            )

        # Required context (parameter level).
        for ctx in p.get("required_context", []) or []:
            cid = context_node(gb, ctx)
            gb.add_edge(
                pid_node, cid, "REQUIRES_CONTEXT",
                label="parameter requires context", confidence="moderate",
                source_files=files, source_tree_ids=trees,
            )

        # Result variations.
        for rv in p.get("result_variations", []) or []:
            rid = f"rv::{pid}::{slug(rv.get('variation_id') or rv.get('result_pattern',''))}"
            ev = rv.get("evidence", {}) or {}
            gb.add_node(
                rid,
                label=rv.get("result_pattern") or rv.get("variation_id") or rid,
                node_type="result_variation",
                domain=domain,
                description=(rv.get("standalone_interpretation") or [""])[0]
                if rv.get("standalone_interpretation")
                else rv.get("result_pattern", ""),
                source_files=files,
                source_tree_ids=trees,
                evidence_strength=normalize_evidence_strength(ev.get("strength")),
                confidence="unknown",
                pipeline_status="ready",
                metadata={
                    "variation_id": rv.get("variation_id"),
                    "direction": rv.get("direction"),
                    "requires_context": rv.get("requires_context"),
                    "guardrail_texts": rv.get("guardrails", []),
                    "cross_modal_links": rv.get("cross_modal_links", []),
                    "human_evidence": ev.get("human_evidence"),
                    "mechanistic_evidence": ev.get("mechanistic_evidence"),
                },
            )
            var_count += 1
            gb.add_edge(
                pid_node, rid, "HAS_VARIATION",
                label="parameter has result variation", confidence="high",
                source_files=files, source_tree_ids=trees,
            )
            for ctx in rv.get("context_needed", []) or []:
                cid = context_node(gb, ctx)
                gb.add_edge(
                    rid, cid, "REQUIRES_CONTEXT",
                    label="result variation requires context",
                    confidence="moderate", source_files=files, source_tree_ids=trees,
                )
            rv_conf = normalize_confidence(ev.get("strength"), default="low")
            for hs in rv.get("candidate_hidden_states", []) or []:
                if norm_id(hs) in hidden_state_ids:
                    gb.add_edge(
                        rid, norm_id(hs), "SUPPORTS_HIDDEN_STATE",
                        label="result variation may support hidden state hypothesis",
                        confidence=rv_conf, source_files=files, source_tree_ids=trees,
                    )
                    gb.add_edge(
                        pid_node, norm_id(hs), "SUPPORTS_HIDDEN_STATE",
                        label="parameter may support hidden state hypothesis",
                        confidence="low", source_files=files, source_tree_ids=trees,
                    )
            # cross-modal "not mechanism-specific" entries reduce confidence.
            for cm in rv.get("cross_modal_links", []) or []:
                meaning = (cm.get("combined_meaning") or "").lower()
                if any(t in meaning for t in ("not mechanism", "not specific", "false reassur", "not equivalent")):
                    for hs in rv.get("candidate_hidden_states", []) or []:
                        if norm_id(hs) in hidden_state_ids:
                            gb.add_edge(
                                rid, norm_id(hs), "CONTRADICTS_OR_REDUCES_CONFIDENCE",
                                label="cross-modal note reduces confidence in hypothesis",
                                confidence="low", source_files=files, source_tree_ids=trees,
                                metadata={"combined_meaning": cm.get("combined_meaning")},
                            )

        # Aliases -> ALIAS_OF when an alias normalizes to another parameter id.
        for alias in p.get("aliases", []) or []:
            alias_id = slug(alias)
            if alias_id and alias_id != pid and alias_id in {norm_id(q["parameter_id"]) for q in params}:
                gb.add_edge(
                    pid_node, alias_id, "ALIAS_OF",
                    label="parameter alias of canonical parameter", confidence="moderate",
                )
    logger.info("Built %d measured_parameter nodes, %d result_variation nodes", len(param_ids), var_count)
    return param_ids


def build_hidden_states(gb: GraphBuilder, hidden_states) -> set:
    hs_ids = set()
    for h in hidden_states.get("hidden_states", []):
        hid = norm_id(h["hidden_state_id"])
        hs_ids.add(hid)
        files = h.get("source_files", [])
        gb.add_node(
            hid,
            label=h.get("display_name") or hid,
            node_type="hidden_state",
            domain=(h.get("domains") or [""])[0] if h.get("domains") else "",
            description=h.get("description", ""),
            source_files=files,
            evidence_strength=normalize_evidence_strength(h.get("confidence")),
            confidence=normalize_node_confidence(h.get("confidence")),
            pipeline_status=normalize_pipeline_status(h.get("pipeline_status")),
            metadata={
                "domains": h.get("domains", []),
                "needs_review": h.get("needs_review"),
                "do_not_infer": h.get("do_not_infer", []),
                "output_type": h.get("output_type"),
                "not_a_diagnosis": h.get("not_a_diagnosis", True),
                "supporting_chains": [c for c in h.get("supporting_chains", []) if c],
            },
        )
        for fname in files:
            ensure_tree_and_file(gb, "", fname)
            gb.add_edge(
                hid, f"file::{fname}", "SUPPORTED_BY_SOURCE",
                label="hidden state hypothesis supported by source file",
                confidence="moderate", source_files=[fname],
            )
    logger.info("Built %d hidden_state nodes", len(hs_ids))
    return hs_ids


def build_inference_chains(gb: GraphBuilder, chains, hidden_state_ids) -> dict:
    chain_index = {}
    for c in chains.get("inference_chains", []):
        cid = norm_id(c["chain_id"])
        node_id = f"chain::{cid}"
        chain_index[cid] = node_id
        fname = c.get("source_file", "")
        tree_id = c.get("source_tree_id", "")
        files = [fname] if fname else []
        trees = [tree_id] if tree_id else []
        gb.add_node(
            node_id,
            label=c.get("chain") or cid,
            node_type="inference_chain",
            description=c.get("chain", ""),
            source_files=files,
            source_tree_ids=trees,
            confidence=normalize_node_confidence(c.get("confidence")),
            evidence_strength=normalize_evidence_strength(c.get("confidence")),
            pipeline_status="ready",
            metadata={
                "chain_id": cid,
                "pattern_name": c.get("pattern_name"),
                "required_sources": c.get("required_sources", []),
                "not_a_diagnosis": c.get("not_a_diagnosis", True),
                "output_type": c.get("output_type"),
            },
        )
        tree_node, _ = ensure_tree_and_file(gb, tree_id, fname)
        if fname:
            gb.add_edge(
                node_id, f"file::{fname}", "SUPPORTED_BY_SOURCE",
                label="inference chain supported by source file",
                confidence=normalize_confidence(c.get("confidence")),
                source_files=files, chain_ids=[cid],
            )
        if tree_node:
            gb.add_edge(
                node_id, tree_node, "DERIVED_FROM",
                label="inference chain derived from source tree",
                confidence=normalize_confidence(c.get("confidence")),
                source_tree_ids=trees, chain_ids=[cid],
            )
        # Chain target -> hidden state (only when target is a canonical hidden state).
        chain_str = c.get("chain", "")
        target = chain_str.split("->")[-1].strip() if "->" in chain_str else cid
        if norm_id(target) in hidden_state_ids:
            gb.add_edge(
                node_id, norm_id(target), "SUPPORTS_HIDDEN_STATE",
                label="inference chain may support hidden state hypothesis",
                confidence=normalize_confidence(c.get("confidence")),
                source_files=files, source_tree_ids=trees, chain_ids=[cid],
            )
    logger.info("Built %d inference_chain nodes", len(chain_index))
    return chain_index


def link_hidden_state_supporting_chains(gb, hidden_states, chain_index, hidden_state_ids) -> int:
    """Authoritative chain -> hidden_state support from each hidden state's record."""
    n = 0
    for h in hidden_states.get("hidden_states", []):
        hid = norm_id(h["hidden_state_id"])
        for sc in h.get("supporting_chains", []):
            sc = norm_id(sc)
            if not sc:
                continue
            node_id = chain_index.get(sc)
            if node_id is None:
                # Chain id referenced but not present as a standalone chain: skip safely.
                continue
            edge = gb.add_edge(
                node_id, hid, "SUPPORTS_HIDDEN_STATE",
                label="inference chain may support hidden state hypothesis",
                confidence=normalize_confidence(h.get("confidence")),
                chain_ids=[sc], source_files=h.get("source_files", []),
            )
            if edge:
                n += 1
    logger.info("Linked %d hidden-state supporting-chain edges", n)
    return n


def link_chain_components(gb, registry, chain_index, hidden_state_ids) -> int:
    """PART_OF_CHAIN: result variation -> chain when candidate_chains references it."""
    chain_str_index = {}
    for cid, node_id in chain_index.items():
        node = gb.nodes[node_id]
        chain_str_index[norm_id(node["metadata"].get("chain_id"))] = node_id
        chain_str_index[slug(node["label"])] = node_id
    n = 0
    for p in registry.get("parameters", []):
        pid = norm_id(p["parameter_id"])
        pid_node = f"param::{pid}" if pid in hidden_state_ids else pid
        files = p.get("source_files", [])
        trees = p.get("source_tree_ids", [])
        for rv in p.get("result_variations", []) or []:
            rid = f"rv::{pid}::{slug(rv.get('variation_id') or rv.get('result_pattern',''))}"
            if not gb.has_node(rid):
                continue
            for cc in rv.get("candidate_chains", []) or []:
                target = cc.split("->")[-1].strip() if "->" in cc else cc
                key = norm_id(target)
                node_id = chain_index.get(key) or chain_str_index.get(slug(cc))
                if node_id:
                    if gb.add_edge(
                        rid, node_id, "PART_OF_CHAIN",
                        label="result variation is part of inference chain",
                        confidence="moderate", source_files=files, source_tree_ids=trees,
                        chain_ids=[gb.nodes[node_id]["metadata"].get("chain_id")],
                    ):
                        n += 1
                    if gb.add_edge(
                        pid_node, node_id, "PART_OF_CHAIN",
                        label="parameter is part of inference chain",
                        confidence="low", source_files=files, source_tree_ids=trees,
                        chain_ids=[gb.nodes[node_id]["metadata"].get("chain_id")],
                    ):
                        n += 1
    logger.info("Linked %d PART_OF_CHAIN edges", n)
    return n


def build_required_measurements(gb, required, chain_index) -> int:
    n = 0
    for r in required.get("required_measurements", []):
        cid = norm_id(r.get("triggering_chain_id", ""))
        node_id = chain_index.get(cid)
        if node_id is None:
            continue
        files = r.get("source_files", [])
        mid = measurement_node(gb, r["required_measurement"], files)
        if gb.add_edge(
            node_id, mid, "RECOMMENDS_MEASUREMENT",
            label="inference chain recommends next-best measurement",
            confidence="moderate", source_files=files, chain_ids=[cid],
        ):
            n += 1
        for fname in files:
            ensure_tree_and_file(gb, "", fname)
            gb.add_edge(
                mid, f"file::{fname}", "SUPPORTED_BY_SOURCE",
                label="required measurement supported by source file",
                confidence="moderate", source_files=[fname],
            )
    logger.info("Built required_measurement edges: %d", n)
    return n


def build_guardrails(gb, guardrails, hidden_state_ids) -> set:
    g_ids = set()
    for g in guardrails.get("guardrails", []):
        gid = norm_id(g["guardrail_id"])
        g_ids.add(gid)
        gb.add_node(
            gid,
            label=gid.replace("_", " ").title(),
            node_type="guardrail",
            domain="guardrail",
            description=g.get("text", ""),
            source_files=g.get("source_files", []),
            evidence_strength="high" if g.get("is_required") else "moderate",
            confidence="high" if g.get("is_required") else "moderate",
            pipeline_status="ready",
            metadata={"is_required": g.get("is_required", False)},
        )
        for fname in g.get("source_files", []):
            ensure_tree_and_file(gb, "", fname)
            gb.add_edge(
                gid, f"file::{fname}", "SUPPORTED_BY_SOURCE",
                label="guardrail supported by source file",
                confidence="high", source_files=[fname], guardrails=[gid],
            )
    logger.info("Built %d guardrail nodes", len(g_ids))
    return g_ids


def bind_guardrails_to_states(gb, guardrail_ids, hidden_state_ids) -> int:
    n = 0
    # Universal guardrails apply to every hidden state (contract requirement).
    for hid in hidden_state_ids:
        for gid in UNIVERSAL_GUARDRAILS:
            if gid in guardrail_ids and gb.add_edge(
                hid, gid, "CONSTRAINED_BY_GUARDRAIL",
                label="hidden state hypothesis constrained by universal guardrail",
                confidence="high", guardrails=[gid],
                metadata={"binding": "universal"},
            ):
                n += 1
    # Definitional guardrail<->state bindings.
    for gid, states in GUARDRAIL_STATE_BINDINGS.items():
        if gid not in guardrail_ids:
            continue
        for hid in states:
            if hid in hidden_state_ids and gb.add_edge(
                hid, gid, "CONSTRAINED_BY_GUARDRAIL",
                label="hidden state hypothesis constrained by definitional guardrail",
                confidence="high", guardrails=[gid],
                metadata={"binding": "definitional"},
            ):
                n += 1
    # context_override_before_mechanism overrides medication_context_override pathway.
    if "context_override_before_mechanism" in guardrail_ids and "medication_context_override" in hidden_state_ids:
        gb.add_edge(
            "context_override_before_mechanism", "medication_context_override",
            "CONTEXT_OVERRIDES",
            label="context override applied before mechanism inference",
            confidence="high", guardrails=["context_override_before_mechanism", "medication_timing_first"],
        )
        n += 1
    logger.info("Bound %d guardrail constraint edges", n)
    return n


def build_static_layer(gb, static_graph, hidden_state_ids) -> None:
    """Integrate the static scientific evidence graph (incl. elevated HR node)."""
    type_map_param = {"observable_marker", "biochemical_marker", "model_feature_node"}
    type_map_state = {
        "physiological_mechanism",
        "neurobiological_affective_bridge",
        "psychological_state_hypothesis",
        "risk_state",
    }
    static_file = "static_scientific_evidence_graph_v0_1.json"
    static_tree = "thsi_static_scientific_evidence_graph_v0_1"
    gb.add_node(
        f"file::{static_file}", label=static_file, node_type="source_file",
        domain="static_scientific_graph",
        description="Static THSI scientific evidence graph (curated, source-referenced).",
        source_files=[static_file], source_tree_ids=[static_tree], pipeline_status="ready",
    )
    gb.add_node(
        f"tree::{static_tree}", label=static_tree, node_type="source_tree",
        domain="static_scientific_graph",
        description="Static scientific evidence graph as a source tree.",
        source_files=[static_file], source_tree_ids=[static_tree], pipeline_status="ready",
    )
    gb.add_edge(
        f"file::{static_file}", f"tree::{static_tree}", "CONTAINS",
        label="source file contains source tree", confidence="high",
        source_files=[static_file], source_tree_ids=[static_tree],
    )

    static_node_type = {}
    for n in static_graph.get("nodes", []):
        nid = norm_id(n["node_id"])
        nt = n["node_type"]
        static_node_type[nid] = nt
        if nt in type_map_param:
            mapped = "measured_parameter"
        elif nt in type_map_state:
            mapped = "hidden_state"
        elif nt == "context_node":
            mapped = "context"
        else:
            mapped = "measured_parameter"
        # Avoid clobbering a richer astronaut-package node of the same id.
        if gb.has_node(nid) and gb.nodes[nid]["type"] != mapped:
            continue
        gb.add_node(
            nid,
            label=n.get("label") or nid,
            node_type=mapped,
            domain=n.get("domain", ""),
            description=n.get("description", ""),
            source_files=[static_file],
            source_tree_ids=[static_tree],
            evidence_strength="moderate",
            confidence="moderate",
            # Static mechanism/state bridges are supplementary in the astronaut
            # pipeline: mark partial so they are exempt from the support-edge rule,
            # while still preserving their static edges for traceability.
            pipeline_status="partial" if mapped == "hidden_state" else "ready",
            metadata={
                "layer": "static_scientific_graph",
                "static_node_type": nt,
                "allowed_as_input": n.get("allowed_as_input"),
                "allowed_as_output": n.get("allowed_as_output"),
                "clinical_diagnosis": n.get("clinical_diagnosis", False),
                "created_from_edges": n.get("created_from_edges", []),
            },
        )
        gb.add_edge(
            nid, f"file::{static_file}", "SUPPORTED_BY_SOURCE",
            label="node supported by static scientific evidence graph",
            confidence="moderate", source_files=[static_file], source_tree_ids=[static_tree],
        )
    # Static sources -> evidence_source nodes.
    for s in static_graph.get("sources", []):
        sid = f"evidence::{norm_id(s['source_id'])}"
        gb.add_node(
            sid,
            label=s.get("title") or s["source_id"],
            node_type="evidence_source",
            domain=s.get("domain", ""),
            description=s.get("main_findings_short", "") or s.get("title", ""),
            evidence_strength=str(s.get("source_type", "")),
            confidence="moderate",
            pipeline_status="ready",
            metadata={
                "source_id": s["source_id"],
                "year": s.get("year"),
                "doi": s.get("doi"),
                "source_type": s.get("source_type"),
                "evidence_strength_score": s.get("evidence_strength_score"),
            },
        )
    # Static edges.
    rel_conf = {"SUPPORTS": "high", "INCREASES_PROBABILITY_OF": "moderate",
                "MAY_INDICATE": "low", "WEAKLY_SUPPORTS": "low"}
    for e in static_graph.get("edges", []):
        src = norm_id(e["source_node"])
        tgt = norm_id(e["target_node"])
        if not (gb.has_node(src) and gb.has_node(tgt)):
            continue
        conf = rel_conf.get(e["relationship_type"], "moderate")
        tgt_type = gb.nodes[tgt]["type"]
        if tgt_type == "hidden_state":
            etype = "SUPPORTS_HIDDEN_STATE"
            label = "scientific evidence may support hidden state hypothesis"
        else:
            etype = "DERIVED_FROM"
            label = "scientific evidence link"
        gb.add_edge(
            src, tgt, etype, label=label, confidence=conf,
            metadata={
                "static_relationship_type": e["relationship_type"],
                "evidence_strength_score": e.get("evidence_strength_score"),
                "source_ids": e.get("source_ids", []),
                "limitations": e.get("limitations", []),
            },
        )
        for sid in e.get("source_ids", []):
            ev_node = f"evidence::{norm_id(sid)}"
            if gb.has_node(ev_node):
                gb.add_edge(
                    src, ev_node, "SUPPORTED_BY_SOURCE",
                    label="link supported by evidence source", confidence=conf,
                )
    # Flagship documented provenance: elevated HR -> low_recovery_state.
    if gb.has_node("elevated_heart_rate_relative_to_baseline") and "low_recovery_state" in hidden_state_ids:
        gb.add_edge(
            "elevated_heart_rate_relative_to_baseline", "low_recovery_state",
            "SUPPORTS_HIDDEN_STATE",
            label="elevated resting HR may support low recovery state hypothesis",
            confidence="moderate",
            metadata={"provenance": "static node created_from_edges: elevated_resting_hr_to_low_recovery_state"},
        )
    logger.info("Integrated static scientific evidence graph layer")


def build_observation_inputs(gb, contract, registry, hidden_state_ids) -> None:
    """observation_input_type + response_type nodes and their edges."""
    for cat in contract.get("accepted_source_categories", []):
        nid = f"input::{norm_id(cat['id'])}"
        examples = cat.get("examples", [])
        gb.add_node(
            nid,
            label=cat.get("display") or cat["id"],
            node_type="observation_input_type",
            domain="data_intake",
            description=cat.get("caveat") or f"Accepted input category: {cat.get('display')}.",
            pipeline_status="ready",
            metadata={"examples": examples, "caveat": cat.get("caveat")},
        )
    # Map input categories to parameters by keyword in measurement_types/sample.
    cat_keywords = {
        "wearable_continuous": ["hr", "hrv", "spo2", "skin", "accelerom", "eda", "wearable"],
        "wearable_sleep": ["sleep", "waso", "actigraph"],
        "self_report_symptom": ["symptom", "vas", "nrs", "self_report", "questionnaire", "self-report"],
        "self_report_behavioral": ["diet", "medication", "activity_log", "behav"],
        "clinical_lab_blood": ["blood", "cbc", "cmp", "crp", "ferritin", "cortisol", "hormone", "serum", "plasma"],
        "clinical_lab_urine": ["urine", "renal", "urinary"],
        "clinical_lab_stool": ["stool", "fecal", "feces"],
        "clinical_lab_saliva": ["saliva", "salivary"],
        "functional_cognitive": ["cognit", "reaction", "attention", "memory", "executive"],
        "sleep_study": ["psg", "eeg", "polysomn"],
        "imaging": ["imaging", "mri", "oct", "ultrasound", "scan"],
        "environmental_sensor": ["co2", "noise", "humidity", "air", "environment", "radiation", "light"],
        "exercise_physiology": ["vo2", "exercise", "cpet", "workload", "lactate"],
        "context_metadata": ["mission", "phase", "context"],
    }
    n_in = 0
    for p in registry.get("parameters", []):
        pid = norm_id(p["parameter_id"])
        pid_node = f"param::{pid}" if pid in hidden_state_ids else pid
        haystack = " ".join(
            [pid, p.get("display_name", "")]
            + p.get("measurement_types", [])
            + p.get("sample_or_sensor", [])
            + p.get("domains", [])
        ).lower()
        for cat_id, kws in cat_keywords.items():
            if any(k in haystack for k in kws):
                if gb.add_edge(
                    f"input::{cat_id}", pid_node, "CAN_ACCEPT_INPUT",
                    label="input category can accept this measured parameter",
                    confidence="moderate",
                ):
                    n_in += 1
    logger.info("Built %d CAN_ACCEPT_INPUT edges", n_in)

    # Response types.
    for rt in contract.get("response_types", []):
        gb.add_node(
            f"response::{norm_id(rt['id'])}",
            label=rt["id"].replace("_", " ").title(),
            node_type="response_type",
            domain="output",
            description=rt.get("description", ""),
            pipeline_status="ready",
        )
    # hidden_state -> hidden_state_hypothesis ; special states to specific responses.
    n_out = 0
    if gb.has_node("response::hidden_state_hypothesis"):
        for hid in hidden_state_ids:
            if gb.add_edge(
                hid, "response::hidden_state_hypothesis", "CAN_OUTPUT_RESPONSE",
                label="hidden state can be reported as traceable hypothesis",
                confidence="high",
            ):
                n_out += 1
    special = {
        "unknown_or_missing_data_state": ["response::missing_data_note", "response::no_inference_possible"],
        "medication_context_override": ["response::context_override_note"],
    }
    for hid, resps in special.items():
        for r in resps:
            if gb.has_node(hid) and gb.has_node(r):
                gb.add_edge(hid, r, "CAN_OUTPUT_RESPONSE",
                            label="hidden state can produce this response", confidence="high")
                n_out += 1
    logger.info("Built %d CAN_OUTPUT_RESPONSE edges", n_out)


def build_data_quality_flags(gb, registry, inventory, hidden_states) -> int:
    """data_quality_flag nodes + NEEDS_REVIEW edges for partial/invalid items."""
    flags = {
        "needs_review_pipeline_status": "Item pipeline status is needs_review or partial; "
        "interpret with caution and seek additional confirming measurements.",
        "json_parse_invalid": "Source file did not parse as valid JSON in the inventory; "
        "data from this file is excluded or flagged.",
        "low_evidence_strength": "Item evidence strength is low; do not treat as mechanism-grade evidence.",
    }
    for fid, text in flags.items():
        gb.add_node(
            f"dqf::{fid}", label=fid.replace("_", " ").title(),
            node_type="data_quality_flag", domain="data_quality",
            description=text, pipeline_status="ready",
            evidence_strength="unknown", confidence="high",
        )
    n = 0
    for nid, node in list(gb.nodes.items()):
        if node["type"] in ("data_quality_flag",):
            continue
        if node["pipeline_status"] in ("partial", "needs_review"):
            if gb.add_edge(
                nid, "dqf::needs_review_pipeline_status", "NEEDS_REVIEW",
                label="node flagged for review", confidence="high",
            ):
                n += 1
        if node["type"] in ("measured_parameter", "result_variation") and node["evidence_strength"] == "low":
            if gb.add_edge(
                nid, "dqf::low_evidence_strength", "NEEDS_REVIEW",
                label="low evidence strength flagged", confidence="moderate",
            ):
                n += 1
    for f in inventory.get("files", []):
        if f.get("json_parse_status") == "invalid":
            fnode = f"file::{f['filename']}"
            if gb.has_node(fnode):
                gb.add_edge(fnode, "dqf::json_parse_invalid", "NEEDS_REVIEW",
                            label="file failed JSON parse", confidence="high")
                n += 1
    logger.info("Built %d NEEDS_REVIEW edges", n)
    return n


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------
def compute_stats(gb: GraphBuilder) -> dict:
    nodes = list(gb.nodes.values())
    edges = list(gb.edges.values())
    degree = Counter()
    for e in edges:
        degree[e["source"]] += 1
        degree[e["target"]] += 1
    top = [
        {"id": nid, "label": gb.nodes[nid]["label"], "type": gb.nodes[nid]["type"], "degree": d}
        for nid, d in degree.most_common(25)
    ]
    nodes_by_type = Counter(n["type"] for n in nodes)
    edges_by_type = Counter(e["type"] for e in edges)
    stats = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes_by_type": dict(sorted(nodes_by_type.items())),
        "edges_by_type": dict(sorted(edges_by_type.items())),
        "top_connected_nodes": top,
        "hidden_state_count": nodes_by_type.get("hidden_state", 0),
        "guardrail_count": nodes_by_type.get("guardrail", 0),
        "measured_parameter_count": nodes_by_type.get("measured_parameter", 0),
        "source_tree_count": nodes_by_type.get("source_tree", 0),
        "needs_review_count": sum(1 for n in nodes if n["pipeline_status"] == "needs_review"),
        "high_confidence_edge_count": sum(1 for e in edges if e["confidence"] == "high"),
        "low_confidence_edge_count": sum(1 for e in edges if e["confidence"] == "low"),
        "partial_node_count": sum(1 for n in nodes if n["pipeline_status"] == "partial"),
        "ready_node_count": sum(1 for n in nodes if n["pipeline_status"] == "ready"),
        "confidence_distribution_edges": dict(Counter(e["confidence"] for e in edges)),
        "pipeline_status_distribution_nodes": dict(Counter(n["pipeline_status"] for n in nodes)),
        "dropped_edges_missing_endpoint": gb._dropped_edges,
    }
    return stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    configure_logging()
    logger.info("=== Building THSI integrated evidence graph v1.0 ===")
    logger.info("Project root: %s", PROJECT_ROOT)

    # Load inputs.
    static_graph = load_json(DATA_DIR / "static_scientific_evidence_graph_v0_1.json")
    registry = load_json(PKG_DIR / "measured_parameter_registry_v1_0.json")
    hidden_states = load_json(PKG_DIR / "hidden_state_candidates_v1_0.json")
    chains = load_json(PKG_DIR / "inference_chains_v1_0.json")
    guardrails = load_json(PKG_DIR / "guardrails_v1_0.json")
    required = load_json(PKG_DIR / "required_measurements_v1_0.json")
    data_sources = load_json(PKG_DIR / "astronaut_data_sources_v1_0.json")
    inventory = load_json(PKG_DIR / "source_file_inventory_v1_0.json")
    contract = load_json(PKG_DIR / "data_intake_contract_v1_0.json")

    gb = GraphBuilder()

    # Hidden states first (their ids define the canonical set used for collision-safe ids).
    hidden_state_ids = build_hidden_states(gb, hidden_states)

    build_source_nodes(gb, data_sources, inventory)
    build_measured_parameters(gb, registry, hidden_state_ids)
    chain_index = build_inference_chains(gb, chains, hidden_state_ids)
    link_hidden_state_supporting_chains(gb, hidden_states, chain_index, hidden_state_ids)
    link_chain_components(gb, registry, chain_index, hidden_state_ids)
    build_required_measurements(gb, required, chain_index)
    guardrail_ids = build_guardrails(gb, guardrails, hidden_state_ids)
    bind_guardrails_to_states(gb, guardrail_ids, hidden_state_ids)
    build_static_layer(gb, static_graph, hidden_state_ids)
    build_observation_inputs(gb, contract, registry, hidden_state_ids)
    build_data_quality_flags(gb, registry, inventory, hidden_states)

    # Validate required coverage during build (log, do not silently pass).
    missing_states = [s for s in REQUIRED_HIDDEN_STATES if s not in gb.nodes]
    missing_guardrails = [g for g in REQUIRED_GUARDRAILS if g not in gb.nodes]
    if missing_states:
        logger.warning("MISSING required hidden states: %s", missing_states)
    else:
        logger.info("All %d required hidden states present", len(REQUIRED_HIDDEN_STATES))
    if missing_guardrails:
        logger.warning("MISSING required guardrails: %s", missing_guardrails)
    else:
        logger.info("All %d required guardrails present", len(REQUIRED_GUARDRAILS))
    if not gb.has_node("elevated_heart_rate_relative_to_baseline"):
        logger.warning("MISSING required node elevated_heart_rate_relative_to_baseline")
    else:
        logger.info("Required node elevated_heart_rate_relative_to_baseline present")

    # Hidden-state support coverage check (ready states must have incoming support).
    incoming_support = defaultdict(int)
    for e in gb.edges.values():
        if e["type"] in ("SUPPORTS_HIDDEN_STATE", "PART_OF_CHAIN"):
            incoming_support[e["target"]] += 1
    unsupported_ready = [
        nid for nid, n in gb.nodes.items()
        if n["type"] == "hidden_state" and n["pipeline_status"] == "ready"
        and incoming_support[nid] == 0
    ]
    if unsupported_ready:
        logger.warning("READY hidden states without support edge: %s", unsupported_ready)
    else:
        logger.info("All ready hidden states have >=1 incoming support edge")

    stats = compute_stats(gb)
    logger.info("Graph stats: %d nodes, %d edges", stats["node_count"], stats["edge_count"])
    logger.info("nodes_by_type: %s", stats["nodes_by_type"])
    logger.info("edges_by_type: %s", stats["edges_by_type"])
    logger.info("Dropped %d edges with a missing endpoint", gb._dropped_edges)

    timestamp = datetime.now(timezone.utc).isoformat()
    nodes_list = [gb.nodes[k] for k in sorted(gb.nodes)]
    edges_list = [gb.edges[k] for k in sorted(gb.edges)]
    metadata = {
        "graph_id": GRAPH_ID,
        "version": GRAPH_VERSION,
        "scientific_name": "Traceable Human State Inference Under Partial Biological Observability",
        "product": "BodyState Mapper",
        "extension": "Astronaut Data Mapping",
        "build_timestamp": timestamp,
        "synthesis_status": "assembled_from_existing_sources",
        "not_a_diagnostic_system": True,
        "core_rule": "Outputs are traceable hidden-state hypotheses with uncertainty, missing-data "
        "notes, guardrails, and next-best measurements. Never a diagnosis.",
        "node_types": sorted(NODE_TYPES),
        "edge_types": sorted(EDGE_TYPES),
        "required_hidden_states_present": [s for s in REQUIRED_HIDDEN_STATES if s in gb.nodes],
        "required_hidden_states_missing": missing_states,
        "required_guardrails_present": [g for g in REQUIRED_GUARDRAILS if g in gb.nodes],
        "required_guardrails_missing": missing_guardrails,
    }

    graph_doc = {"metadata": metadata, "stats": stats, "nodes": nodes_list, "edges": edges_list}

    PKG_DIR.mkdir(parents=True, exist_ok=True)
    out_graph = PKG_DIR / "integrated_evidence_graph_v1_0.json"
    out_nodes = PKG_DIR / "integrated_evidence_graph_nodes_v1_0.json"
    out_edges = PKG_DIR / "integrated_evidence_graph_edges_v1_0.json"
    out_stats = PKG_DIR / "integrated_evidence_graph_stats_v1_0.json"

    out_graph.write_text(json.dumps(graph_doc, indent=2, ensure_ascii=False), encoding="utf-8")
    out_nodes.write_text(
        json.dumps({"metadata": metadata, "nodes": nodes_list}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    out_edges.write_text(
        json.dumps({"metadata": metadata, "edges": edges_list}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    out_stats.write_text(
        json.dumps({"metadata": metadata, "stats": stats}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    for p in (out_graph, out_nodes, out_edges, out_stats):
        logger.info("Wrote %s (%d bytes)", p.relative_to(PROJECT_ROOT), p.stat().st_size)

    logger.info("=== Build complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
