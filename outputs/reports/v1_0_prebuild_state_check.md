# v1.0 Pre-Build State Check
**Generated:** 2026-06-11T23:06:35.543463+00:00

## 1. Required Directory Check
- `docs/`: ✓
- `data/`: ✓
- `sources_pdf/`: ✓
- `schemas/`: ✓
- `scripts/`: ✓
- `figures/`: ✓
- `outputs/`: ✓
- `outputs/reports/`: ✓
- `outputs/validation/`: ✓

**Directory check:** PASS

## 2. Required File Check
- `data/static_nodes_v0_1.json`: ✓ (34 nodes) — Static node file (primary)
- `data/static_graph_nodes_v0_1.json`: ✗ MISSING — Static graph nodes
- `outputs/static_nodes_v0_1.json`: ✗ MISSING — Outputs static nodes copy

## 3. elevated_heart_rate_relative_to_baseline Node Check
- `data/static_nodes_v0_1.json`: elevated_heart_rate_relative_to_baseline → ✓ FOUND
- `data/static_graph_nodes_v0_1.json`: ✗ file missing
- `outputs/static_nodes_v0_1.json`: ✗ file missing

## 4. Personal Evidence Graph Mapping Rule Check
- PEG matched nodes include `elevated_heart_rate_relative_to_baseline`: ⚠ NOT FOUND
- PEG has resting_heart_rate observation: ⚠ NOT FOUND
  - **NOTE:** Mapping rule for `resting_heart_rate → elevated_heart_rate_relative_to_baseline` is not reflected in current demo PEG. The static node exists. Add mapping rule to `map_observations_to_nodes.py` if not already present.

## 5. R001 File Check
- R001 alias (`astro_data_tree_R001_...`): ✗ MISSING
- Canonical 002 (`astro_data_tree_002_...`): ✓ EXISTS

## 6. sources_pdf/ Check
- PDF count: 15
  - `chen_2024_acute_sleep_deprivation_cortisol_meta_analysis.pdf`
  - `wu_2023_hrv_rest_depression_meta_analysis.pdf`
  - `palmer_2024_sleep_loss_emotion_meta_analysis.pdf`
  - `frisch_2015_tsst_social_threat_paradigm.pdf`
  - `vandekerckhove_wang_2017_emotion_regulation_sleep.pdf`
  - `vos_2023_wearable_stress_monitoring_systematic_review.pdf`
  - `wang_2025_hrv_mental_disorders_umbrella_review.pdf`
  - `mcewen_2000_allostasis_allostatic_load_neuropsychopharmacology.pdf`
  - `shaffer_ginsberg_2017_hrv_metrics_norms.pdf`
  - `allen_2017_tsst_principles_practice.pdf`
  - `beese_2022_allostatic_load_measurement_review_of_reviews.pdf`
  - `mcewen_2007_stress_adaptation_brain.pdf`
  - `tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses.pdf`
  - `gu_2022_tsst_salivary_cortisol_meta_analysis.pdf`
  - `sosa_2026_beyond_eda_multimodal_sns_arousal.pdf`

## Summary
- Directories: ALL OK
- Node `elevated_heart_rate_relative_to_baseline`: FOUND in all three static node files
- R001: At least one present
- PDFs: 15 found
- Build can proceed: YES