# Consolidated Validation Summary v1.0
**Generated:** 2026-06-11T23:06:35.543463+00:00

## Results Overview
| Script | Status |
|--------|--------|
| `validate_static_graph` | ✓ PASS |
| `validate_personal_evidence_graph` | ✓ PASS |
| `validate_inference_output` | ✓ PASS |
| `validate_astronaut_mapping_package_v1_0` | ✓ PASS |

**Total:** 4 | Passed: 4 | Failed: 0 | Skipped: 0 | Error/Timeout: 0

## validate_static_graph
```
=== THSI Static Graph Validation Report ===

Counts:
  sources: 15
  PDFs found: 15
  edges: 21
  nodes: 34

Passed (6):
  ✓ All 15 registry PDFs present in <project root>/sources_pdf
  ✓ No duplicate source_id values
  ✓ No direct observable_marker → psychological_state_hypothesis edges
  ✓ No duplicate edge_id values
  ✓ No duplicate node_id values
  ✓ All validation rule groups satisfied

Validation status: PASSED

```
**stderr:**
```
2026-06-11T19:06:35 [INFO] Loaded 15 registry entries, 21 edges, 34 nodes
2026-06-11T19:06:35 [INFO] Validation passed.

```

## validate_personal_evidence_graph
```
=== THSI Personal Evidence Graph Validation ===

Passed (5):
  ✓ All 3 raw observations have required fields
  ✓ All 3 derived markers have supporting_observations
  ✓ All 3 inference input observations reference static nodes
  ✓ Personal evidence graph JSON exists: <project root>/outputs/demo_personal_evidence_graph_v0_1.json
  ✓ Inference input JSON exists: <project root>/outputs/demo_inference_input_from_personal_graph_v0_1.json

Validation status: PASSED

```
**stderr:**
```
2026-06-11T19:06:35 [INFO] Personal evidence graph validation passed

```

## validate_inference_output
```
=== THSI Inference Output Validation ===

Validation status: PASSED

```
**stderr:**
```
2026-06-11T19:06:35 [INFO] Inference output validation passed

```

## validate_astronaut_mapping_package_v1_0
```
ource, marked partial/needs_review
  [WARN] hidden_state_traceability: viral_reactivation_context: no source, marked partial/needs_review
  [WARN] hidden_state_traceability: perceptual_neurobehavioral_fatigue: no source, marked partial/needs_review
  [PASS] hidden_state_traceability: migraine_phenotype_branch: traceable
  [WARN] hidden_state_traceability: iron_deficiency_oxygen_delivery_branch: no source, marked partial/needs_review
  [PASS] hidden_state_traceability: renal_stone_risk_branch: traceable
  [PASS] hidden_state_traceability: team_behavioral_risk: traceable
  [PASS] hidden_state_traceability: SANS_risk_branch: traceable
  [WARN] hidden_state_traceability: wearable_sleep_false_reassurance: no source, marked partial/needs_review
  [WARN] hidden_state_traceability: acute_sleep_loss: no source, marked partial/needs_review
  [WARN] hidden_state_traceability: hyperventilation_hypocapnia_state: no source, marked partial/needs_review
  [WARN] hidden_state_traceability: sleep_fragmentation_recovery_failure: no source, marked partial/needs_review
  [WARN] hidden_state_traceability: bone_unloading_loss: no source, marked partial/needs_review
  [PASS] hidden_state_traceability: radiation_biological_effect_branch: traceable
  [PASS] hidden_state_traceability: low_recovery_state: traceable
  [PASS] hidden_state_traceability: heat_strain: traceable
  [WARN] hidden_state_traceability: metabolic_strain: no source, marked partial/needs_review

[CHECK 17] No hidden state claims final diagnosis...
  [PASS] no_diagnosis_claim: No hidden states claim diagnosis as final conclusion

============================================================
VALIDATION COMPLETE
  Passes:   76
  Warnings: 19
  Failures: 0
============================================================
[WRITE] <project root>/outputs/validation/astronaut_mapping_package_validation_v1_0.json
[WRITE] <project root>/outputs/validation/astronaut_mapping_package_validation_v1_0.md

```
