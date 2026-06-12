# BodyState Mapper / THSI — Astronaut Data Mapping v1.0 Knowledge Package

**Scientific name:** Traceable Human State Inference Under Partial Biological Observability  
**Product name:** BodyState Mapper — Astronaut Data Mapping Extension  
**Build timestamp:** 2026-06-11T23:06:35.543463+00:00

## What This Package Is

This is the v1.0 knowledge package for the BodyState Mapper / THSI system. It is NOT a diagnostic system.
Outputs are traceable, uncertainty-aware hidden-state hypotheses, missing-data notes, context overrides,
guardrails, and next-best-measurement recommendations. No output constitutes a medical diagnosis.

## Package Files

| File | Description |
|------|-------------|
| `astronaut_data_sources_v1_0.json` | Inventory of all astronaut data tree and repair module source files |
| `measured_entities_v1_0.json` | All 487 measured parameter entities with metadata |
| `measured_parameter_registry_v1_0.json` | Full parameter registry with result variations, cross-modal links, guardrails |
| `measured_parameter_registry_summary_v1_0.md` | Human-readable registry summary |
| `result_variation_trees_v1_0.json` | Result variation trees per parameter |
| `cross_modal_links_v1_0.json` | Cross-modal inference links |
| `hidden_state_candidates_v1_0.json` | 34 hidden state candidate definitions |
| `inference_chains_v1_0.json` | 245 inference chains |
| `guardrails_v1_0.json` | 194 guardrails including all 23 required |
| `required_measurements_v1_0.json` | Next-best-measurement recommendations |
| `mission_phase_interpretation_v1_0.json` | Mission phase-specific interpretation notes |
| `all_to_all_matrix_v1_0.json` | All-to-all parameter inference matrix |
| `validation_protocol_v1_0.json` | Package validation protocol |
| `data_intake_contract_v1_0.json` | Data intake contract and observation schema |
| `source_file_inventory_v1_0.json` | Full source file inventory |

## Core Principle

NOT a diagnostic system. All outputs are:
- Traceable to source files and tree IDs
- Uncertainty-aware (confidence levels required)
- Hypothesis-based (hidden states, not diagnoses)
- Subject to mandatory guardrails
- Inclusive of next-best-measurement recommendations when data is insufficient

## Core Workflow

```
raw multimodal data
  → normalized observation (data_intake_contract)
  → parameter registry lookup
  → result variation assignment
  → context/guardrail check
  → hidden-state scoring
  → next-measurement recommendation
  → traceable report
```

## Mandatory Guardrails (excerpt)

- `unknown_is_not_negative_evidence`: Missing data ≠ absent state
- `single_marker_never_equals_mechanism`: No single biomarker establishes mechanism
- `medication_timing_first`: Evaluate medications before inferring mechanism
- `PEM_not_normal_fatigue`: PEM is not ordinary post-exertional tiredness
- `wearable_sleep_stage_not_PSG`: Wearable sleep stages ≠ polysomnography
- `recommend_next_measurement_when_uncertain`: Output next-best-measurement, not forced conclusion

## Version

v1.0 — Initial production knowledge package assembly.
