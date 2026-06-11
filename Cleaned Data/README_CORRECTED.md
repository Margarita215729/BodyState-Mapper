# Cleaned Data Corrected

Corrected package generated for BodyState Mapper / Astronaut Data Mapping.

## Corrections applied

- Removed macOS metadata entries (`__MACOSX/` and `._*`).
- Removed duplicate convenience alias `astro_002_blood_systemic_repair.cleaned.json`; kept canonical file `astro_data_tree_002_blood_systemic_CBC_CMP_electrolytes_kidney_liver_repair.cleaned.json`.
- Repaired `autonomic_stress_axis.json` by replacing the invalid JSON content with the valid content from `autonomic_stress_axis_fixed.json`.
- Kept `autonomic_stress_axis_fixed.json` and `autonomic_stress_axis_curated.json` as useful support modules.
- Added `source_file_inventory_v1_0.json` for downstream pipeline routing.

## Contents

- Primary astronaut source trees: `astro_data_tree_001` through `astro_data_tree_036`, plus `astro_data_tree_005A`.
- Repair modules: R002 pain/headache/injury, R003 pulmonary/body composition, R004 PSG/EEG sleep architecture, and canonical repaired 002 blood systemic tree.
- Base BodyState Mapper scientific series: `series_004b` through `series_050`.
- Curated/fixed support modules for earlier core axes.
- Documentation notes.

## Validation

All `.json` files in this corrected package were parsed successfully after repair.

Generated: 2026-06-11T21:56:39
