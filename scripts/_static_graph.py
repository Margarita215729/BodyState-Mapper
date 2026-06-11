"""Shared loaders, node inference, validation, and graph helpers for static evidence graph scripts."""

from __future__ import annotations

import csv
import json
import logging
import re
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from _project_paths import (
    EDGE_FIELDS,
    EDGES_CSV,
    EDGES_JSON,
    GRAPH_ID,
    GRAPH_JSON,
    GRAPH_VERSION,
    NODE_FIELDS,
    NODES_CSV,
    NODES_JSON,
    REGISTRY_CSV,
    REGISTRY_JSON,
    SOURCES_PDF_DIR,
)

logger = logging.getLogger(__name__)

EXPLICIT_NODE_TYPES: dict[str, str] = {
    "reduced_hrv_relative_to_baseline": "observable_marker",
    "low_resting_hrv": "observable_marker",
    "persistent_low_hrv": "observable_marker",
    "increased_eda": "observable_marker",
    "skin_conductance_response": "observable_marker",
    "sleep_loss": "observable_marker",
    "sleep_restriction": "observable_marker",
    "sleep_disturbance": "observable_marker",
    "acute_sleep_deprivation": "observable_marker",
    "salivary_cortisol_increase": "observable_marker",
    "wearable_multimodal_features": "model_feature_node",
    "social_evaluative_threat_context": "context_node",
    "TSST_protocol_features": "context_node",
    "environmental_stressor_context": "context_node",
    "autonomic_regulation_shift": "physiological_mechanism",
    "sympathetic_arousal": "physiological_mechanism",
    "sympathetic_nervous_system_activation": "physiological_mechanism",
    "recovery_deficit": "physiological_mechanism",
    "hpa_axis_activation": "physiological_mechanism",
    "acute_psychosocial_stress_response": "physiological_mechanism",
    "stress_adaptation_response": "physiological_mechanism",
    "allostasis": "physiological_mechanism",
    "allostatic_load": "physiological_mechanism",
    "multi_system_dysregulation": "physiological_mechanism",
    "parasympathetic_withdrawal": "physiological_mechanism",
    "repeated_stress_responses": "physiological_mechanism",
    "mental_health_related_autonomic_dysregulation": "physiological_mechanism",
    "acute_arousal_state": "physiological_mechanism",
    "cortisol_elevation": "biochemical_marker",
    "emotion_regulation_impairment": "neurobiological_affective_bridge",
    "increased_emotional_reactivity": "neurobiological_affective_bridge",
    "negative_mood_increase": "neurobiological_affective_bridge",
    "reduced_positive_affect": "neurobiological_affective_bridge",
    "stress_vulnerability": "neurobiological_affective_bridge",
    "depressive_like_pattern_contextual": "neurobiological_affective_bridge",
    "fatigue_like_state": "psychological_state_hypothesis",
    "anxiety_like_arousal_state": "psychological_state_hypothesis",
    "irritability_vulnerability": "psychological_state_hypothesis",
    "low_positive_affect_state": "psychological_state_hypothesis",
    "acute_stress_like_state": "psychological_state_hypothesis",
    "cognitive_load_or_arousal_state": "psychological_state_hypothesis",
    "health_risk_state": "risk_state",
    "stress_state_prediction": "risk_state",
    "chronic_stress_physiology": "risk_state",
    "biomarker_composite": "model_feature_node",
}

BRIDGE_NODE_TYPES = frozenset(
    {"neurobiological_affective_bridge", "physiological_mechanism"}
)

INTERMEDIATE_NODE_TYPES = frozenset(
    {
        "physiological_mechanism",
        "neurobiological_affective_bridge",
        "biochemical_marker",
        "risk_state",
    }
)

INPUT_NODE_TYPES = frozenset(
    {"observable_marker", "context_node", "model_feature_node"}
)

OUTPUT_NODE_TYPES = frozenset(
    {
        "physiological_mechanism",
        "neurobiological_affective_bridge",
        "risk_state",
        "psychological_state_hypothesis",
    }
)

FORBIDDEN_NODE_SUBSTRINGS = ("diagnosis", "disorder", "disease")
FORBIDDEN_TARGET_SUFFIXES = ("_diagnosis",)


@dataclass
class ValidationReport:
    """Structured validation outcome for static graph checks."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    passed: list[str] = field(default_factory=list)
    source_count: int = 0
    pdf_count: int = 0
    edge_count: int = 0
    node_count: int = 0

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def parse_source_ids(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    text = str(raw).strip()
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def normalize_field_value(value: Any) -> Any:
    if isinstance(value, list):
        return value
    if value is None:
        return ""
    return value


def load_registry_json(path: Path = REGISTRY_JSON) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Registry JSON must be an array: {path}")
    return data


def load_registry_csv(path: Path = REGISTRY_CSV) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_edges_json(path: Path = EDGES_JSON) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Edges JSON must be an array: {path}")
    return data


def load_edges_csv(path: Path = EDGES_CSV) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows: list[dict[str, Any]] = []
        for row in csv.DictReader(handle):
            if not any(v.strip() for v in row.values() if v):
                continue
            item = dict(row)
            item["source_ids"] = parse_source_ids(item.get("source_ids", ""))
            if item.get("evidence_strength_score"):
                try:
                    item["evidence_strength_score"] = int(item["evidence_strength_score"])
                except ValueError:
                    pass
            if item.get("confidence_prior"):
                try:
                    item["confidence_prior"] = float(item["confidence_prior"])
                except ValueError:
                    pass
            rows.append(item)
        return rows


def load_nodes_json(path: Path = NODES_JSON) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Nodes JSON must be an array: {path}")
    return data


def load_graph_artifact(path: Path = GRAPH_JSON) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Graph JSON must be an object: {path}")
    return data


def load_graph_nodes_and_edges(
    path: Path = GRAPH_JSON,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    graph = load_graph_artifact(path)
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if not isinstance(nodes, list):
        raise ValueError(f"Graph nodes must be an array: {path}")
    if not isinstance(edges, list):
        raise ValueError(f"Graph edges must be an array: {path}")
    return nodes, edges, graph


def load_observations_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Observations JSON must be an array: {path}")
    return data


def node_id_to_label(node_id: str) -> str:
    return re.sub(r"\s+", " ", node_id.replace("_", " ")).strip().title()


def infer_node_type(node_id: str) -> str:
    if node_id in EXPLICIT_NODE_TYPES:
        return EXPLICIT_NODE_TYPES[node_id]
    normalized = node_id.lower()
    if normalized.endswith("_like_state") or normalized.endswith("_vulnerability"):
        return "psychological_state_hypothesis"
    if normalized.endswith("_context") or "protocol_features" in normalized:
        return "context_node"
    if "prediction" in normalized or "composite" in normalized:
        return "model_feature_node"
    if "cortisol" in normalized or "biomarker" in normalized:
        return "biochemical_marker"
    if normalized.endswith("_risk_state") or normalized == "health_risk_state":
        return "risk_state"
    if any(
        token in normalized
        for token in (
            "impairment",
            "reactivity",
            "mood",
            "affect",
            "vulnerability",
        )
    ):
        return "neurobiological_affective_bridge"
    if any(
        token in normalized
        for token in (
            "arousal",
            "activation",
            "regulation",
            "response",
            "dysregulation",
            "deficit",
            "load",
            "allostasis",
        )
    ):
        return "physiological_mechanism"
    if any(
        token in normalized
        for token in ("sleep", "hrv", "eda", "heart_rate", "wearable")
    ):
        return "observable_marker"
    return "physiological_mechanism"


def node_has_forbidden_clinical_token(node_id: str) -> bool:
    normalized = node_id.lower()
    return any(token in normalized for token in FORBIDDEN_NODE_SUBSTRINGS)


def build_node_domain_map(
    edges: list[dict[str, Any]],
    registry: list[dict[str, Any]],
) -> dict[str, str]:
    domains: dict[str, set[str]] = defaultdict(set)

    for edge in edges:
        domain = str(edge.get("domain", "")).strip()
        if not domain:
            continue
        for node_key in ("source_node", "target_node"):
            node_id = str(edge.get(node_key, "")).strip()
            if node_id:
                domains[node_id].add(domain)

    for source in registry:
        domain = str(source.get("domain", "")).strip()
        if not domain:
            continue
        supported = source.get("supported_nodes", [])
        if isinstance(supported, str):
            supported = [s.strip() for s in supported.split(";") if s.strip()]
        if isinstance(supported, list):
            for node_id in supported:
                node_id = str(node_id).strip()
                if node_id:
                    domains[node_id].add(domain)

    resolved: dict[str, str] = {}
    for node_id, values in domains.items():
        resolved[node_id] = sorted(values)[0]
    return resolved


def build_node_edge_map(edges: list[dict[str, Any]]) -> dict[str, list[str]]:
    edge_map: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        edge_id = str(edge.get("edge_id", "")).strip()
        if not edge_id:
            continue
        for node_key in ("source_node", "target_node"):
            node_id = str(edge.get(node_key, "")).strip()
            if node_id:
                edge_map[node_id].add(edge_id)
    return {node_id: sorted(edge_ids) for node_id, edge_ids in edge_map.items()}


def node_description(node_id: str, node_type: str) -> str:
    role_by_type = {
        "observable_marker": "Observable input signal referenced in evidence edges.",
        "physiological_mechanism": "Physiological mechanism node used as an intermediate bridge.",
        "biochemical_marker": "Biochemical marker node used in mechanism pathways.",
        "neurobiological_affective_bridge": "Neurobiological/affective bridge between physiology and cautious state hypotheses.",
        "psychological_state_hypothesis": "Cautious psychological state hypothesis; not a clinical diagnosis.",
        "risk_state": "Risk-oriented physiological burden state; not a clinical diagnosis.",
        "context_node": "Contextual factor required for edge interpretation.",
        "model_feature_node": "Model or composite feature node used in inference pathways.",
        "methodological_node": "Methodological or protocol construct referenced in evidence.",
    }
    return (
        f"{node_id_to_label(node_id)}: "
        f"{role_by_type.get(node_type, 'Graph node referenced in static evidence edges.')}"
    )


def build_nodes(
    edges: list[dict[str, Any]],
    registry: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    node_ids: set[str] = set()
    for edge in edges:
        source = str(edge.get("source_node", "")).strip()
        target = str(edge.get("target_node", "")).strip()
        if source:
            node_ids.add(source)
        if target:
            node_ids.add(target)

    domain_map = build_node_domain_map(edges, registry)
    edge_map = build_node_edge_map(edges)
    nodes: list[dict[str, Any]] = []
    for node_id in sorted(node_ids):
        node_type = infer_node_type(node_id)
        nodes.append(
            {
                "node_id": node_id,
                "node_type": node_type,
                "label": node_id_to_label(node_id),
                "domain": domain_map.get(node_id, ""),
                "description": node_description(node_id, node_type),
                "allowed_as_input": node_type in INPUT_NODE_TYPES,
                "allowed_as_output": node_type in OUTPUT_NODE_TYPES,
                "clinical_diagnosis": False,
                "created_from_edges": edge_map.get(node_id, []),
            }
        )
    return nodes


def write_nodes_csv(path: Path, nodes: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=NODE_FIELDS)
        writer.writeheader()
        for node in nodes:
            row = {field: node.get(field, "") for field in NODE_FIELDS}
            row["allowed_as_input"] = str(bool(node.get("allowed_as_input"))).lower()
            row["allowed_as_output"] = str(bool(node.get("allowed_as_output"))).lower()
            row["clinical_diagnosis"] = str(bool(node.get("clinical_diagnosis"))).lower()
            edge_ids = node.get("created_from_edges", [])
            row["created_from_edges"] = ";".join(edge_ids) if edge_ids else ""
            writer.writerow(row)
    logger.info("Wrote nodes CSV (%d rows): %s", len(nodes), path)


def write_nodes_json(path: Path, nodes: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(nodes, indent=2) + "\n", encoding="utf-8")
    logger.info("Wrote nodes JSON (%d rows): %s", len(nodes), path)


def write_nodes_md(path: Path, nodes: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Static Nodes v0.1",
        "",
        "Typed node registry inferred from `static_scientific_edges_v0_1.json`.",
        "All nodes have `clinical_diagnosis: false`. Psychological outputs are state hypotheses only.",
        "",
        f"**Total nodes:** {len(nodes)}",
        "",
        "| node_id | node_type | label | domain | allowed_as_input | allowed_as_output | edges |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for node in nodes:
        edge_ids = node.get("created_from_edges", [])
        edge_count = len(edge_ids) if isinstance(edge_ids, list) else 0
        lines.append(
            f"| {node['node_id']} | {node['node_type']} | {node['label']} | "
            f"{node.get('domain', '')} | {node.get('allowed_as_input')} | "
            f"{node.get('allowed_as_output')} | {edge_count} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote nodes MD (%d rows): %s", len(nodes), path)


def build_graph_artifact(
    registry: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    validation_status: str = "passed",
) -> dict[str, Any]:
    direct_diagnostic = sum(
        1
        for edge in edges
        if infer_node_type(str(edge.get("source_node", ""))) == "observable_marker"
        and infer_node_type(str(edge.get("target_node", "")))
        == "psychological_state_hypothesis"
    )
    return {
        "graph_id": GRAPH_ID,
        "version": GRAPH_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "nodes": nodes,
        "edges": edges,
        "sources": registry,
        "validation_summary": {
            "source_count": len(registry),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "direct_diagnostic_edges": direct_diagnostic,
            "validation_status": validation_status,
        },
    }


def write_graph_json(path: Path, graph: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    logger.info("Wrote graph JSON: %s", path)


def field_is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, str):
        return bool(value.strip())
    return True


def parse_confidence_prior(value: Any) -> float | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def path_has_intermediate_bridge(node_path: list[str], node_types: dict[str, str]) -> bool:
    if len(node_path) < 2:
        return False
    for node_id in node_path[:-1]:
        if node_types.get(node_id, infer_node_type(node_id)) in BRIDGE_NODE_TYPES:
            return True
    return False


def validate_static_graph(
    registry: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    nodes: list[dict[str, Any]] | None = None,
    pdf_dir: Path = SOURCES_PDF_DIR,
) -> ValidationReport:
    from _project_paths import EDGE_REQUIRED_FIELDS, REGISTRY_REQUIRED_FIELDS

    report = ValidationReport()
    report.source_count = len(registry)
    report.edge_count = len(edges)

    if nodes is None:
        nodes = build_nodes(edges, registry)
    report.node_count = len(nodes)

    node_by_id = {n["node_id"]: n for n in nodes}
    node_types = {n["node_id"]: n["node_type"] for n in nodes}

    source_ids_seen: set[str] = set()
    pdf_names_seen: set[str] = set()
    pdf_files_found = 0

    for index, row in enumerate(registry):
        prefix = f"registry[{index}]"
        for req_field in REGISTRY_REQUIRED_FIELDS:
            value = row.get(req_field)
            if value is None or (isinstance(value, str) and not value.strip()):
                report.errors.append(f"{prefix}: missing required field '{req_field}'")

        source_id = str(row.get("source_id", "")).strip()
        if not source_id:
            continue
        if source_id in source_ids_seen:
            report.errors.append(f"{prefix}: duplicate source_id '{source_id}'")
        source_ids_seen.add(source_id)

        expected_pdf = f"{source_id}.pdf"
        pdf_filename = str(row.get("pdf_filename", "")).strip()
        if pdf_filename != expected_pdf:
            report.errors.append(
                f"{prefix} source_id={source_id}: "
                f"pdf_filename must be '{expected_pdf}', got '{pdf_filename}'"
            )
        if pdf_filename in pdf_names_seen:
            report.errors.append(
                f"{prefix} source_id={source_id}: duplicate pdf_filename"
            )
        pdf_names_seen.add(pdf_filename)

        pdf_path = pdf_dir / expected_pdf
        if pdf_path.is_file():
            pdf_files_found += 1
        else:
            report.errors.append(
                f"{prefix} source_id={source_id}: missing PDF at {pdf_path}"
            )

    report.pdf_count = pdf_files_found
    if pdf_files_found == len(registry) and len(registry) > 0:
        report.passed.append(
            f"All {len(registry)} registry PDFs present in {pdf_dir}"
        )
    elif pdf_files_found > 0:
        report.warnings.append(
            f"Only {pdf_files_found}/{len(registry)} registry PDFs found in {pdf_dir}"
        )

    if len(source_ids_seen) == len(registry) and not any(
        "duplicate source_id" in e for e in report.errors
    ):
        report.passed.append("No duplicate source_id values")

    registry_ids = source_ids_seen

    edge_ids_seen: set[str] = set()
    direct_diagnostic_edges = 0

    for index, edge in enumerate(edges):
        edge_label = f"edge[{index}] edge_id={edge.get('edge_id', '?')}"

        for req_field in EDGE_REQUIRED_FIELDS:
            value = edge.get(req_field)
            if req_field == "source_ids":
                if not parse_source_ids(value):
                    report.errors.append(f"{edge_label}: missing source_ids")
                continue
            if not field_is_present(value):
                report.errors.append(f"{edge_label}: missing required field '{req_field}'")

        edge_id = str(edge.get("edge_id", "")).strip()
        if edge_id:
            if edge_id in edge_ids_seen:
                report.errors.append(f"{edge_label}: duplicate edge_id '{edge_id}'")
            edge_ids_seen.add(edge_id)

        source_node = str(edge.get("source_node", "")).strip()
        target_node = str(edge.get("target_node", "")).strip()
        if not source_node:
            report.errors.append(f"{edge_label}: missing source_node")
        if not target_node:
            report.errors.append(f"{edge_label}: missing target_node")

        if node_has_forbidden_clinical_token(target_node):
            report.errors.append(
                f"{edge_label}: forbidden clinical token in target node '{target_node}'"
            )
        if node_has_forbidden_clinical_token(source_node):
            report.errors.append(
                f"{edge_label}: forbidden clinical token in source node '{source_node}'"
            )

        if any(target_node.endswith(suffix) for suffix in FORBIDDEN_TARGET_SUFFIXES):
            report.errors.append(
                f"{edge_label}: forbidden target ending '_diagnosis' ({target_node})"
            )

        confidence = parse_confidence_prior(edge.get("confidence_prior"))
        if confidence is None:
            report.errors.append(
                f"{edge_label}: confidence_prior must be numeric between 0 and 1"
            )
        elif confidence < 0 or confidence > 1:
            report.errors.append(
                f"{edge_label}: confidence_prior {confidence} out of range [0, 1]"
            )

        if source_node and source_node not in node_by_id:
            report.errors.append(
                f"{edge_label}: source_node '{source_node}' not in static_nodes_v0_1"
            )
        if target_node and target_node not in node_by_id:
            report.errors.append(
                f"{edge_label}: target_node '{target_node}' not in static_nodes_v0_1"
            )

        source_type = node_types.get(source_node) or infer_node_type(source_node)
        target_type = node_types.get(target_node) or infer_node_type(target_node)
        if (
            source_type == "observable_marker"
            and target_type == "psychological_state_hypothesis"
        ):
            direct_diagnostic_edges += 1
            report.errors.append(
                f"{edge_label}: forbidden direct observable_marker → "
                f"psychological_state_hypothesis ({source_node} → {target_node})"
            )

        if target_type == "psychological_state_hypothesis" and source_type not in (
            INTERMEDIATE_NODE_TYPES | {"psychological_state_hypothesis"}
        ):
            report.errors.append(
                f"{edge_label}: psychological_state_hypothesis '{target_node}' "
                f"requires intermediate mechanism/bridge source, got '{source_node}' "
                f"({source_type})"
            )

        for source_id in parse_source_ids(edge.get("source_ids")):
            if source_id not in registry_ids:
                report.errors.append(
                    f"{edge_label}: unknown source_id '{source_id}' not in registry"
                )

    if direct_diagnostic_edges == 0:
        report.passed.append("No direct observable_marker → psychological_state_hypothesis edges")

    if len(edge_ids_seen) == len(edges) and not any(
        "duplicate edge_id" in e for e in report.errors
    ):
        report.passed.append("No duplicate edge_id values")

    node_ids_seen: set[str] = set()
    for node in nodes:
        node_id = node.get("node_id", "")
        if node_id in node_ids_seen:
            report.errors.append(f"nodes: duplicate node_id '{node_id}'")
        node_ids_seen.add(node_id)

        if node.get("clinical_diagnosis") is not False:
            report.errors.append(
                f"node '{node_id}': clinical_diagnosis must be false"
            )
        if node_has_forbidden_clinical_token(node_id):
            report.errors.append(
                f"node '{node_id}': forbidden clinical token in node_id"
            )

        edge_refs = node.get("created_from_edges", [])
        if not edge_refs:
            report.warnings.append(f"node '{node_id}': empty created_from_edges")

    if len(node_ids_seen) == len(nodes):
        report.passed.append("No duplicate node_id values")

    hypothesis_nodes = [
        n["node_id"]
        for n in nodes
        if n["node_type"] == "psychological_state_hypothesis"
    ]
    adjacency = build_adjacency(edges)
    for hyp_node in hypothesis_nodes:
        has_valid_incoming = False
        for edge in edges:
            if str(edge.get("target_node", "")).strip() != hyp_node:
                continue
            source = str(edge.get("source_node", "")).strip()
            source_type = node_types.get(source, infer_node_type(source))
            if source_type in INTERMEDIATE_NODE_TYPES:
                has_valid_incoming = True
                break
        if not has_valid_incoming:
            report.errors.append(
                f"psychological_state_hypothesis '{hyp_node}' has no incoming "
                "edge from mechanism/bridge/risk/biochemical intermediate"
            )

    if not report.errors:
        report.passed.append("All validation rule groups satisfied")

    return report


def build_adjacency(edges: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    adjacency: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        source = str(edge.get("source_node", "")).strip()
        if source:
            adjacency[source].append(edge)
    return adjacency


def collect_paths_bfs(
    start_nodes: list[str],
    adjacency: dict[str, list[dict[str, Any]]],
    node_types: dict[str, str],
    max_depth: int = 4,
    target_type: str | None = None,
    require_bridge_for: set[str] | None = None,
) -> tuple[set[str], list[dict[str, Any]]]:
    reachable: set[str] = set(start_nodes)
    paths: list[dict[str, Any]] = []
    queue: deque[tuple[str, list[str], list[dict[str, Any]], bool]] = deque()

    for node in start_nodes:
        queue.append((node, [node], [], False))

    while queue:
        current, node_path, edge_path, crossed_bridge = queue.popleft()
        if len(edge_path) >= max_depth:
            continue

        for edge in adjacency.get(current, []):
            target = str(edge.get("target_node", "")).strip()
            if not target or target in node_path:
                continue

            target_node_type = node_types.get(target, infer_node_type(target))
            next_crossed_bridge = crossed_bridge or (
                target_node_type in BRIDGE_NODE_TYPES
            )

            new_node_path = node_path + [target]
            new_edge_path = edge_path + [edge]
            reachable.add(target)

            if target_type is None or target_node_type == target_type:
                if require_bridge_for and target in require_bridge_for:
                    if next_crossed_bridge:
                        paths.append(
                            {
                                "target_node": target,
                                "node_path": new_node_path,
                                "edge_path": new_edge_path,
                            }
                        )
                elif target_type is None:
                    paths.append(
                        {
                            "target_node": target,
                            "node_path": new_node_path,
                            "edge_path": new_edge_path,
                        }
                    )
                else:
                    paths.append(
                        {
                            "target_node": target,
                            "node_path": new_node_path,
                            "edge_path": new_edge_path,
                        }
                    )

            queue.append((target, new_node_path, new_edge_path, next_crossed_bridge))

    return reachable, paths


def aggregate_list_field(values: list[Any]) -> list[str]:
    aggregated: list[str] = []
    seen: set[str] = set()
    for value in values:
        if isinstance(value, list):
            for item in value:
                text = str(item).strip()
                if text and text not in seen:
                    seen.add(text)
                    aggregated.append(text)
        else:
            text = str(value).strip()
            if text and text not in seen:
                seen.add(text)
                aggregated.append(text)
    return aggregated


def format_query_path(node_path: list[str], edge_path: list[dict[str, Any]]) -> dict[str, Any]:
    limitations: list[Any] = []
    risks: list[Any] = []
    for edge in edge_path:
        limitations.append(edge.get("limitations"))
        risks.append(edge.get("risk_of_overinterpretation"))

    return {
        "node_sequence": node_path,
        "edge_sequence": [edge.get("edge_id") for edge in edge_path],
        "source_ids": sorted(
            {
                sid
                for edge in edge_path
                for sid in parse_source_ids(edge.get("source_ids"))
            }
        ),
        "relationship_types": [edge.get("relationship_type") for edge in edge_path],
        "confidence_priors": [edge.get("confidence_prior") for edge in edge_path],
        "evidence_strength_scores": [
            edge.get("evidence_strength_score") for edge in edge_path
        ],
        "limitations": aggregate_list_field(limitations),
        "risk_of_overinterpretation": aggregate_list_field(risks),
    }


def query_graph(
    input_node_ids: list[str],
    edges: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    max_depth: int = 4,
) -> dict[str, Any]:
    node_types = {n["node_id"]: n["node_type"] for n in nodes}
    adjacency = build_adjacency(edges)

    reachable, all_paths = collect_paths_bfs(
        input_node_ids, adjacency, node_types, max_depth=max_depth
    )

    valid_paths: list[dict[str, Any]] = []
    for path_entry in all_paths:
        node_path = path_entry["node_path"]
        target = path_entry["target_node"]
        target_type = node_types.get(target, infer_node_type(target))

        if target_type == "psychological_state_hypothesis":
            if not path_has_intermediate_bridge(node_path, node_types):
                continue

        valid_paths.append(format_query_path(node_path, path_entry["edge_path"]))

    def nodes_of_type(type_name: str) -> list[str]:
        return sorted(
            node_id
            for node_id in reachable
            if node_types.get(node_id, infer_node_type(node_id)) == type_name
        )

    hypothesis_nodes = nodes_of_type("psychological_state_hypothesis")
    hypothesis_from_valid_paths = sorted(
        {p["node_sequence"][-1] for p in valid_paths if p["node_sequence"]}
    )

    return {
        "input_nodes": input_node_ids,
        "max_depth": max_depth,
        "reachable_nodes": sorted(reachable),
        "reachable_mechanisms": nodes_of_type("physiological_mechanism"),
        "reachable_bridge_nodes": nodes_of_type("neurobiological_affective_bridge"),
        "reachable_risk_states": nodes_of_type("risk_state"),
        "reachable_psychological_state_hypotheses": [
            n for n in hypothesis_nodes if n in hypothesis_from_valid_paths
        ],
        "paths": valid_paths,
    }


def print_validation_report(report: ValidationReport) -> None:
    print("=== THSI Static Graph Validation Report ===")
    print()
    print("Counts:")
    print(f"  sources: {report.source_count}")
    print(f"  PDFs found: {report.pdf_count}")
    print(f"  edges: {report.edge_count}")
    print(f"  nodes: {report.node_count}")
    print()
    if report.passed:
        print(f"Passed ({len(report.passed)}):")
        for item in report.passed:
            print(f"  ✓ {item}")
        print()
    if report.warnings:
        print(f"Warnings ({len(report.warnings)}):")
        for item in report.warnings:
            print(f"  ⚠ {item}")
        print()
    if report.errors:
        print(f"Errors ({len(report.errors)}):")
        for item in report.errors:
            print(f"  ✗ {item}")
        print()
    status = "PASSED" if report.ok else "FAILED"
    print(f"Validation status: {status}")
