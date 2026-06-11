"""Path scoring for THSI Inference Engine v0.1."""

from __future__ import annotations

import logging
import math
from typing import Any

from _static_graph import aggregate_list_field, parse_source_ids

logger = logging.getLogger(__name__)

EVIDENCE_STRENGTH_MODIFIER: dict[int, float] = {
    5: 1.00,
    4: 0.85,
    3: 0.70,
    2: 0.50,
    1: 0.30,
}

RISK_PENALTY: dict[str, float] = {
    "low": 1.00,
    "medium": 0.85,
    "high": 0.65,
    "critical": 0.35,
}

RISK_ORDER: dict[str, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}


def evidence_strength_modifier(score: Any) -> float:
    try:
        key = int(score)
    except (TypeError, ValueError):
        logger.warning("Invalid evidence_strength_score %r; using modifier 0.30", score)
        return EVIDENCE_STRENGTH_MODIFIER[1]
    return EVIDENCE_STRENGTH_MODIFIER.get(key, EVIDENCE_STRENGTH_MODIFIER[1])


def risk_penalty(risk_level: Any) -> float:
    text = str(risk_level or "medium").strip().lower()
    if text not in RISK_PENALTY:
        logger.warning("Unknown risk_of_overinterpretation %r; using medium penalty", risk_level)
        text = "medium"
    return RISK_PENALTY[text]


def normalize_confidence_prior(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        logger.warning("Invalid confidence_prior %r; using 0.0", value)
        return 0.0
    return max(0.0, min(1.0, confidence))


def score_edge(
    edge: dict[str, Any],
    *,
    apply_quality_score: bool,
    quality_score: float,
) -> dict[str, Any]:
    confidence_prior = normalize_confidence_prior(edge.get("confidence_prior"))
    strength_score = edge.get("evidence_strength_score")
    strength_modifier = evidence_strength_modifier(strength_score)
    risk_level = str(edge.get("risk_of_overinterpretation", "medium")).strip().lower()
    penalty = risk_penalty(risk_level)

    edge_score = confidence_prior * strength_modifier * penalty
    quality_applied: float | None = None
    if apply_quality_score:
        quality_applied = max(0.0, min(1.0, float(quality_score)))
        edge_score *= quality_applied

    return {
        "edge_id": edge.get("edge_id"),
        "confidence_prior": confidence_prior,
        "evidence_strength_score": strength_score,
        "evidence_strength_modifier": strength_modifier,
        "risk_of_overinterpretation": risk_level,
        "risk_penalty": penalty,
        "quality_score_applied": quality_applied,
        "edge_score": edge_score,
    }


def geometric_mean(values: list[float]) -> float:
    if not values:
        return 0.0
    if any(v <= 0 for v in values):
        return 0.0
    return math.exp(sum(math.log(v) for v in values) / len(values))


def highest_risk_level(levels: list[str]) -> str:
    if not levels:
        return "medium"
    return max(levels, key=lambda level: RISK_ORDER.get(level, 1))


def score_path(
    node_path: list[str],
    edge_path: list[dict[str, Any]],
    *,
    quality_score: float = 1.0,
) -> dict[str, Any]:
    if not edge_path:
        return {
            "path_score": 0.0,
            "score_components": [],
            "weakest_edge": None,
            "highest_risk_edge": None,
            "source_ids_used": [],
            "limitations_used": [],
        }

    score_components: list[dict[str, Any]] = []
    edge_scores: list[float] = []
    weakest_edge: dict[str, Any] | None = None
    highest_risk_edge: dict[str, Any] | None = None
    risk_levels: list[str] = []

    for index, edge in enumerate(edge_path):
        component = score_edge(
            edge,
            apply_quality_score=(index == 0),
            quality_score=quality_score,
        )
        score_components.append(component)
        edge_scores.append(component["edge_score"])
        risk_levels.append(component["risk_of_overinterpretation"])

        if weakest_edge is None or component["edge_score"] < weakest_edge["edge_score"]:
            weakest_edge = component

        current_risk = RISK_ORDER.get(component["risk_of_overinterpretation"], 1)
        highest_risk = (
            RISK_ORDER.get(highest_risk_edge["risk_of_overinterpretation"], 1)
            if highest_risk_edge
            else -1
        )
        if current_risk > highest_risk:
            highest_risk_edge = component

    path_score = geometric_mean(edge_scores)
    source_ids_used = sorted(
        {
            sid
            for edge in edge_path
            for sid in parse_source_ids(edge.get("source_ids"))
        }
    )
    limitations_used = aggregate_list_field(
        [edge.get("limitations") for edge in edge_path]
    )

    logger.debug(
        "Scored path %s -> %s: path_score=%.4f, edges=%d",
        node_path[0] if node_path else "?",
        node_path[-1] if node_path else "?",
        path_score,
        len(edge_path),
    )

    return {
        "path_score": path_score,
        "score_components": score_components,
        "weakest_edge": weakest_edge,
        "highest_risk_edge": highest_risk_edge,
        "source_ids_used": source_ids_used,
        "limitations_used": limitations_used,
        "risk_of_overinterpretation": highest_risk_level(risk_levels),
    }


def hypothesis_score_from_paths(path_scores: list[float]) -> float:
    if not path_scores:
        return 0.0
    return max(path_scores)
