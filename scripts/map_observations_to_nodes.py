#!/usr/bin/env python3
"""Rule-based mapping from raw personal observations to static graph derived markers."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

CONTEXT_ONLY_DERIVED_NODES = frozenset(
    {
        "illness_symptoms_present",
        "recent_exercise_context",
    }
)

DEVIATION_MODIFIERS = {
    "strong": 1.0,
    "moderate": 0.75,
    "weak": 0.5,
}


def baseline_quality_modifier(sample_count: int | None) -> float:
    if sample_count is None:
        return 0.3
    if sample_count >= 21:
        return 1.0
    if sample_count >= 7:
        return 0.75
    return 0.5


def compute_confidence(
    observation_quality: float,
    baseline_modifier: float,
    deviation_strength: str,
) -> float:
    deviation_modifier = DEVIATION_MODIFIERS.get(deviation_strength, 0.5)
    return min(1.0, observation_quality * baseline_modifier * deviation_modifier)


def classify_below_median_deviation(
    below_amount: float,
    median: float,
    std: float,
    pct_threshold: float,
    std_threshold: float = 1.0,
) -> str | None:
    if below_amount <= 0:
        return None
    pct = below_amount / median if median else 0.0
    std_units = below_amount / std if std else 0.0
    if std_units < std_threshold and pct < pct_threshold:
        return None
    if std_units >= 2.0 or pct >= pct_threshold * 1.6:
        return "strong"
    if std_units >= 1.5 or pct >= pct_threshold * 1.2:
        return "moderate"
    return "weak"


def classify_above_median_deviation(
    above_amount: float,
    median: float,
    std: float,
    pct_threshold: float,
    std_threshold: float = 1.0,
) -> str | None:
    if above_amount <= 0:
        return None
    pct = above_amount / median if median else 0.0
    std_units = above_amount / std if std else 0.0
    if std_units < std_threshold and pct < pct_threshold:
        return None
    if std_units >= 2.0 or pct >= pct_threshold * 1.67:
        return "strong"
    if std_units >= 1.5 or pct >= pct_threshold * 1.33:
        return "moderate"
    return "weak"


def get_baseline_marker(
    baseline: dict[str, Any],
    signal_type: str,
) -> dict[str, Any] | None:
    markers = baseline.get("markers", {})
    if not isinstance(markers, dict):
        return None
    marker = markers.get(signal_type)
    if isinstance(marker, dict) and marker:
        return marker
    return None


def build_derived_marker(
    *,
    marker_id: str,
    observation: dict[str, Any],
    derived_node: str,
    derivation_rule: str,
    baseline_used: dict[str, Any] | None,
    deviation_score: float,
    deviation_strength: str,
    extra_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    obs_quality = float(observation.get("quality_score", 0.0))
    sample_count = None
    if baseline_used is not None:
        raw_count = baseline_used.get("sample_count")
        if raw_count is not None:
            sample_count = int(raw_count)

    baseline_mod = baseline_quality_modifier(sample_count)
    confidence = compute_confidence(obs_quality, baseline_mod, deviation_strength)

    context = dict(observation.get("context", {}))
    if extra_context:
        context.update(extra_context)
    context["deviation_strength"] = deviation_strength
    context["context_only"] = derived_node in CONTEXT_ONLY_DERIVED_NODES

    marker = {
        "marker_id": marker_id,
        "subject_id": str(observation.get("subject_id", "")),
        "timestamp": str(observation.get("timestamp", "")),
        "derived_node": derived_node,
        "derivation_rule": derivation_rule,
        "supporting_observations": [str(observation.get("observation_id", ""))],
        "baseline_used": baseline_used,
        "deviation_score": round(deviation_score, 4),
        "confidence": round(confidence, 4),
        "quality_score": obs_quality,
        "context": context,
        "notes": str(observation.get("notes", "")),
    }
    logger.info(
        "Derived marker %s: %s -> %s (confidence=%.4f, deviation=%s)",
        marker_id,
        observation.get("observation_id"),
        derived_node,
        confidence,
        deviation_strength,
    )
    return marker


def map_sleep_duration(
    observation: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any] | None:
    value = float(observation["value"])
    marker_stats = get_baseline_marker(baseline, "sleep_duration")
    if not marker_stats:
        logger.warning(
            "No sleep_duration baseline for observation %s",
            observation.get("observation_id"),
        )
        return None

    median = float(marker_stats["median"])
    hours_below = median - value
    if hours_below >= 1.5:
        derived_node = "sleep_loss"
        deviation_strength = "strong"
        rule = (
            f"sleep_duration {value}h is {hours_below:.1f}h below baseline median "
            f"{median}h (>= 1.5h threshold) -> sleep_loss"
        )
    elif hours_below >= 1.0:
        derived_node = "sleep_restriction"
        deviation_strength = "moderate"
        rule = (
            f"sleep_duration {value}h is {hours_below:.1f}h below baseline median "
            f"{median}h (1.0-1.5h range) -> sleep_restriction"
        )
    else:
        return None

    return build_derived_marker(
        marker_id=f"derived_{observation['observation_id']}",
        observation=observation,
        derived_node=derived_node,
        derivation_rule=rule,
        baseline_used=marker_stats,
        deviation_score=hours_below,
        deviation_strength=deviation_strength,
        extra_context={
            "observed_value": value,
            "baseline_median": median,
            "hours_below_median": round(hours_below, 2),
        },
    )


def map_hrv_rmssd(
    observation: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any] | None:
    value = float(observation["value"])
    marker_stats = get_baseline_marker(baseline, "hrv_rmssd")
    if not marker_stats:
        logger.warning(
            "No hrv_rmssd baseline for observation %s",
            observation.get("observation_id"),
        )
        return None

    median = float(marker_stats["median"])
    std = float(marker_stats.get("std", 0) or 0)
    below = median - value
    deviation_strength = classify_below_median_deviation(
        below, median, std, pct_threshold=0.25
    )
    if not deviation_strength:
        return None

    rule = (
        f"hrv_rmssd {value}ms is below baseline median {median}ms by "
        f"{below:.1f}ms (>= 1 std or >= 25%) -> reduced_hrv_relative_to_baseline"
    )
    deviation_score = below / std if std else below / median if median else below

    return build_derived_marker(
        marker_id=f"derived_{observation['observation_id']}",
        observation=observation,
        derived_node="reduced_hrv_relative_to_baseline",
        derivation_rule=rule,
        baseline_used=marker_stats,
        deviation_score=deviation_score,
        deviation_strength=deviation_strength,
        extra_context={
            "observed_value": value,
            "baseline_median": median,
            "below_median_ms": round(below, 2),
        },
    )


def map_resting_heart_rate(
    observation: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any] | None:
    value = float(observation["value"])
    marker_stats = get_baseline_marker(baseline, "resting_heart_rate")
    if not marker_stats:
        logger.warning(
            "No resting_heart_rate baseline for observation %s",
            observation.get("observation_id"),
        )
        return None

    median = float(marker_stats["median"])
    std = float(marker_stats.get("std", 0) or 0)
    above = value - median
    deviation_strength = classify_above_median_deviation(
        above, median, std, pct_threshold=0.15
    )
    if not deviation_strength:
        return None

    rule = (
        f"resting_heart_rate {value}bpm is above baseline median {median}bpm by "
        f"{above:.1f}bpm (>= 1 std or >= 15%) -> elevated_heart_rate_relative_to_baseline"
    )
    deviation_score = above / std if std else above / median if median else above

    return build_derived_marker(
        marker_id=f"derived_{observation['observation_id']}",
        observation=observation,
        derived_node="elevated_heart_rate_relative_to_baseline",
        derivation_rule=rule,
        baseline_used=marker_stats,
        deviation_score=deviation_score,
        deviation_strength=deviation_strength,
        extra_context={
            "observed_value": value,
            "baseline_median": median,
            "above_median_bpm": round(above, 2),
        },
    )


def map_eda(
    observation: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any] | None:
    value = float(observation["value"])
    marker_stats = get_baseline_marker(baseline, "eda")
    if not marker_stats:
        logger.warning(
            "No eda baseline for observation %s",
            observation.get("observation_id"),
        )
        return None

    median = float(marker_stats["median"])
    std = float(marker_stats.get("std", 0) or 0)
    above = value - median
    deviation_strength = classify_above_median_deviation(
        above, median, std, pct_threshold=0.30
    )
    if not deviation_strength:
        return None

    rule = (
        f"eda {value} is above baseline median {median} by {above:.2f} "
        f"(>= 1 std or >= 30%) -> increased_eda"
    )
    deviation_score = above / std if std else above / median if median else above

    return build_derived_marker(
        marker_id=f"derived_{observation['observation_id']}",
        observation=observation,
        derived_node="increased_eda",
        derivation_rule=rule,
        baseline_used=marker_stats,
        deviation_score=deviation_score,
        deviation_strength=deviation_strength,
        extra_context={
            "observed_value": value,
            "baseline_median": median,
            "above_median": round(above, 3),
        },
    )


def map_salivary_cortisol(
    observation: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any] | None:
    value = float(observation["value"])
    marker_stats = get_baseline_marker(baseline, "salivary_cortisol")
    context = observation.get("context", {})

    if marker_stats:
        median = float(marker_stats["median"])
        std = float(marker_stats.get("std", 0) or 0)
        above = value - median
        if std <= 0 or above < std:
            return None
        deviation_strength = "strong" if above >= 2 * std else "moderate"
        rule = (
            f"salivary_cortisol {value} is above baseline median {median} by "
            f">= 1 std -> salivary_cortisol_increase"
        )
        deviation_score = above / std
        return build_derived_marker(
            marker_id=f"derived_{observation['observation_id']}",
            observation=observation,
            derived_node="salivary_cortisol_increase",
            derivation_rule=rule,
            baseline_used=marker_stats,
            deviation_score=deviation_score,
            deviation_strength=deviation_strength,
            extra_context={
                "observed_value": value,
                "baseline_median": median,
                "above_median": round(above, 3),
            },
        )

    if context.get("above_reference_range") is True:
        rule = (
            "salivary_cortisol above reference range with no personal baseline "
            "-> salivary_cortisol_increase"
        )
        return build_derived_marker(
            marker_id=f"derived_{observation['observation_id']}",
            observation=observation,
            derived_node="salivary_cortisol_increase",
            derivation_rule=rule,
            baseline_used=None,
            deviation_score=1.0,
            deviation_strength="weak",
            extra_context={
                "observed_value": value,
                "above_reference_range": True,
            },
        )

    logger.info(
        "Skipping salivary_cortisol observation %s: no baseline and "
        "above_reference_range not set",
        observation.get("observation_id"),
    )
    return None


def map_illness_symptoms(observation: dict[str, Any]) -> dict[str, Any] | None:
    if observation.get("value") is not True:
        return None
    return build_derived_marker(
        marker_id=f"derived_{observation['observation_id']}",
        observation=observation,
        derived_node="illness_symptoms_present",
        derivation_rule="illness_symptoms value is true -> illness_symptoms_present (context only)",
        baseline_used=None,
        deviation_score=1.0,
        deviation_strength="moderate",
        extra_context={"alternative_explanation": True},
    )


def map_recent_exercise(observation: dict[str, Any]) -> dict[str, Any] | None:
    if observation.get("value") is not True:
        return None
    return build_derived_marker(
        marker_id=f"derived_{observation['observation_id']}",
        observation=observation,
        derived_node="recent_exercise_context",
        derivation_rule="recent_exercise value is true -> recent_exercise_context (context only)",
        baseline_used=None,
        deviation_score=1.0,
        deviation_strength="moderate",
        extra_context={"alternative_explanation": True},
    )


SIGNAL_MAPPERS: dict[str, Any] = {
    "sleep_duration": map_sleep_duration,
    "hrv_rmssd": map_hrv_rmssd,
    "resting_heart_rate": map_resting_heart_rate,
    "eda": map_eda,
    "salivary_cortisol": map_salivary_cortisol,
    "illness_symptoms": map_illness_symptoms,
    "recent_exercise": map_recent_exercise,
}


def map_observations_to_derived_markers(
    raw_observations: list[dict[str, Any]],
    baseline: dict[str, Any],
) -> list[dict[str, Any]]:
    """Apply all mapping rules and return derived markers for matched observations."""
    derived: list[dict[str, Any]] = []
    logger.info(
        "Mapping %d raw observations against baseline for subject %s",
        len(raw_observations),
        baseline.get("subject_id"),
    )

    for observation in raw_observations:
        obs_id = observation.get("observation_id", "?")
        signal_type = str(observation.get("signal_type", "")).strip()
        mapper = SIGNAL_MAPPERS.get(signal_type)
        if mapper is None:
            logger.info(
                "No mapping rule for signal_type '%s' (observation %s)",
                signal_type,
                obs_id,
            )
            continue

        try:
            if signal_type in ("illness_symptoms", "recent_exercise"):
                marker = mapper(observation)
            else:
                marker = mapper(observation, baseline)
        except (TypeError, ValueError, KeyError) as exc:
            logger.error(
                "Failed to map observation %s (%s): %s",
                obs_id,
                signal_type,
                exc,
            )
            continue

        if marker is not None:
            derived.append(marker)

    logger.info("Produced %d derived markers from %d raw observations", len(derived), len(raw_observations))
    return derived


def derived_markers_to_inference_observations(
    derived_markers: list[dict[str, Any]],
    raw_observations: list[dict[str, Any]],
    static_node_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Convert derived markers to personal_observation records for run_inference.py."""
    raw_by_id = {
        str(obs.get("observation_id")): obs for obs in raw_observations
    }
    inference_observations: list[dict[str, Any]] = []

    for marker in derived_markers:
        derived_node = str(marker.get("derived_node", "")).strip()
        if derived_node in CONTEXT_ONLY_DERIVED_NODES:
            logger.info(
                "Skipping context-only derived marker %s (%s) for inference input",
                marker.get("marker_id"),
                derived_node,
            )
            continue

        if static_node_ids is not None and derived_node not in static_node_ids:
            logger.warning(
                "Skipping derived marker %s: derived_node '%s' not in static graph",
                marker.get("marker_id"),
                derived_node,
            )
            continue

        supporting_ids = marker.get("supporting_observations", [])
        source_obs = raw_by_id.get(str(supporting_ids[0])) if supporting_ids else {}
        source = str(source_obs.get("source", "derived_feature"))

        inference_obs = {
            "observation_id": str(marker.get("marker_id")),
            "subject_id": str(marker.get("subject_id")),
            "timestamp": str(marker.get("timestamp")),
            "observed_node": derived_node,
            "value": True,
            "value_type": "derived_marker",
            "unit": None,
            "source": source,
            "quality_score": float(marker.get("confidence", 0.0)),
            "context": dict(marker.get("context", {})),
            "notes": (
                f"Derived from raw observation(s) {', '.join(supporting_ids)} via "
                f"{marker.get('derivation_rule', 'rule-based mapping')}. "
                f"{marker.get('notes', '')}"
            ).strip(),
        }
        inference_observations.append(inference_obs)
        logger.info(
            "Inference observation %s: observed_node=%s confidence=%.4f",
            inference_obs["observation_id"],
            derived_node,
            inference_obs["quality_score"],
        )

    return inference_observations
