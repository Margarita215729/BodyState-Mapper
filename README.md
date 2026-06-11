# BodyState Mapper

BodyState Mapper is the project workspace for **THSI** (Temporal Human State Inference): a source-traceable, conservative knowledge layer that links observables and biological mechanisms using literature-backed relationships.

**Version:** v0.1 (static scientific evidence graph and evidence source registry).

## Purpose

The static graph connects markers and mechanisms (for example HRV, cortisol, sleep loss, autonomic regulation) with explicit `source_id` citations. It supports inference paths such as observable → mechanism → neurobiological bridge → cautious psychological hypothesis.

## Core rule: no direct biomarker-to-diagnosis

**Forbidden:** any edge that jumps from a biomarker or observable directly to a psychological or clinical diagnosis.

Psychological hypotheses must pass through intermediate biological or neurobiological mechanism nodes. Validation scripts reject targets ending in `_diagnosis` and explicit clinical endpoints (for example `panic_attack`).

## Folder structure

```
BodyState Mapper/
├── docs/              Project documentation (PDF)
├── sources_pdf/       Scientific source PDFs named {source_id}.pdf
├── data/              Registry, edges, nodes, built graph, manifests
├── schemas/           JSON Schema for registry, nodes, edges, graph
├── scripts/           Validate, build, query, and export tooling
├── figures/           Static evidence graph diagrams (SVG, PNG, MMD, DOT)
├── outputs/           Generated exports and build artifacts
└── README.md
```

## Data files (v0.1)

| File | Role |
|------|------|
| `data/evidence_source_registry_v0_1.*` | Fifteen curated sources with metadata and `pdf_filename` |
| `data/static_scientific_edges_v0_1.*` | Literature-backed edges between graph nodes |
| `data/static_nodes_v0_1.*` | Node definitions |
| `data/static_scientific_evidence_graph_v0_1.json` | Combined graph artifact |
| `data/pdf_filename_manifest_v0_1.csv` | PDF rename / locate status per source |

Place each registry PDF in `sources_pdf/` as `{source_id}.pdf` (see manifest for legacy filenames).

## Static Scientific Evidence Graph v0.1

The static graph is a validated, machine-readable knowledge layer for THSI. It links observables and contexts to physiological mechanisms, neurobiological/affective bridges, risk states, and cautious psychological state hypotheses — always with literature traceability via `source_id`.

### What the graph contains

| Artifact | Location | Description |
|----------|----------|-------------|
| Evidence sources | `data/evidence_source_registry_v0_1.*` | 15 curated papers with metadata |
| Source PDFs | `sources_pdf/{source_id}.pdf` | One PDF per registry entry |
| Edges | `data/static_scientific_edges_v0_1.*` | Literature-backed directed relationships |
| Nodes | `data/static_nodes_v0_1.*` | Typed nodes inferred from edges |
| Built graph | `data/static_scientific_evidence_graph_v0_1.json` | Combined registry + nodes + edges |
| Schemas | `schemas/static_*.schema.json` | JSON Schema for nodes, edges, graph |

### No direct diagnosis rule

**Forbidden:** biomarker or observable → clinical/psychological diagnosis (e.g. `low_hrv → depression_diagnosis`).

**Allowed path:** observable → physiological mechanism → neurobiological/affective bridge → cautious state hypothesis (e.g. `fatigue_like_state`, `anxiety_like_arousal_state`).

Validation rejects direct `observable_marker → psychological_state_hypothesis` edges, nodes containing `diagnosis`/`disorder`/`disease`, and psychological hypotheses not reached through intermediate mechanism or bridge nodes.

### Commands

Validate the full graph (registry, PDFs, edges, nodes, typing rules):

```bash
python3 scripts/validate_static_graph.py
```

Build nodes and the combined graph artifact:

```bash
python3 scripts/build_static_graph.py
```

Run an example query from sleep/EDA/HRV observables:

```bash
python3 scripts/query_static_graph.py \
  --start sleep_loss,increased_eda,reduced_hrv_relative_to_baseline \
  --max-depth 4 \
  --output outputs/example_static_graph_query_v0_1.json \
  --markdown outputs/example_static_graph_query_v0_1.md
```

Path constants live in `scripts/_project_paths.py` (`PROJECT_ROOT` is the BodyState Mapper root).

## Inference Engine v0.1

The inference engine is a graph-based, evidence-traceable prototype (not a machine learning model). It accepts personal observations mapped to static graph node IDs and returns reachable mechanisms, bridge nodes, cautious psychological state hypotheses, scored evidence paths, source citations, limitations, and conservative interpretations.

### Purpose

- Translate observed signals (wearable, manual, derived) into literature-backed mechanism and state-hypothesis pathways.
- Enforce the no-direct-diagnosis rule: paths must traverse intermediate mechanism or bridge nodes before any psychological state hypothesis.
- Produce auditable JSON and human-readable Markdown reports with preliminary confidence scores.

### Input format

Observations conform to `schemas/personal_observation.schema.json`:

| Field | Description |
|-------|-------------|
| `observation_id` | Unique record identifier |
| `subject_id` | Person identifier |
| `timestamp` | ISO 8601 datetime |
| `observed_node` | Must match a `node_id` in `static_nodes_v0_1.json` |
| `value` | boolean, number, string, or object |
| `value_type` | `boolean`, `numeric`, `categorical`, `derived_marker`, or `manual_report` |
| `source` | `wearable`, `manual_input`, `lab_test`, `derived_feature`, `questionnaire`, or `unknown` |
| `quality_score` | 0–1 weight; observations with `quality_score <= 0` are excluded |
| `context` | Structured metadata object |
| `notes` | Free-text notes |

Demo observations: `data/demo_observations_v0_1.json` (sleep loss, increased EDA, reduced HRV relative to baseline).

### Scoring

Per edge:

```
edge_score = confidence_prior × evidence_strength_modifier × risk_penalty
```

- **Evidence strength modifier:** 5→1.00, 4→0.85, 3→0.70, 2→0.50, 1→0.30
- **Risk penalty:** low→1.00, medium→0.85, high→0.65, critical→0.35
- **First edge** from an observed node is additionally multiplied by the observation `quality_score`.

Per path: `path_score` = geometric mean of edge scores.

Per hypothesis: `hypothesis_score` = maximum `path_score` across supporting paths.

### Run demo

```bash
python3 scripts/run_inference.py \
  --graph data/static_scientific_evidence_graph_v0_1.json \
  --observations data/demo_observations_v0_1.json \
  --max-depth 4 \
  --output-json outputs/demo_inference_result_v0_1.json \
  --output-md outputs/demo_inference_report_v0_1.md
```

Validate outputs:

```bash
python3 scripts/validate_inference_output.py \
  --json outputs/demo_inference_result_v0_1.json \
  --markdown outputs/demo_inference_report_v0_1.md
```

### Interpreting output

- **Hypotheses** (e.g. `fatigue_like_state`, `anxiety_like_arousal_state`) are cautious state descriptions, not clinical labels.
- **Scores** are preliminary weights derived from edge confidence, evidence strength, overinterpretation risk, and observation quality — not probabilities of disorder.
- **Supporting paths** show the observable → mechanism → bridge → hypothesis chain with `source_id` traceability.
- **Limitations** and **warnings** must be read alongside any hypothesis; additional context may change conclusions.

### Scientific warning

**This output is not a medical diagnosis.** All psychological outputs are cautious state hypotheses. The engine supports, may indicate, or is compatible with mechanism-linked interpretations — it does not detect, diagnose, prove, or identify any disorder.

## Personal Evidence Graph v0.1

The personal evidence graph layer maps **raw personal observations** to **static graph node IDs** using **personal baselines**, then produces inference-engine-ready observations. Mapping is rule-based and transparent — no machine learning and no medical diagnoses.

### Pipeline

```
raw observations
  → personal baseline comparison
  → derived markers
  → matched static graph nodes
  → personal evidence graph
  → inference engine input
```

### Artifacts

| File | Role |
|------|------|
| `schemas/raw_observation.schema.json` | Raw signal observations (`signal_type`, `value`, `quality_score`, …) |
| `schemas/personal_baseline.schema.json` | Personal baseline statistics per marker |
| `schemas/derived_marker.schema.json` | Rule-derived markers mapped to graph `node_id`s |
| `schemas/personal_evidence_graph.schema.json` | Combined personal graph artifact |
| `data/demo_raw_observations_v0_1.json` | Demo raw signals (sleep, HRV, EDA) |
| `data/demo_personal_baseline_v0_1.json` | Demo baseline medians and sample counts |
| `outputs/demo_personal_evidence_graph_v0_1.json` | Built personal evidence graph |
| `outputs/demo_inference_input_from_personal_graph_v0_1.json` | Observations for `run_inference.py` |

### Mapping rules (v0.1)

| Signal | Condition | Derived node |
|--------|-----------|--------------|
| `sleep_duration` | ≥1.5 h below baseline median | `sleep_loss` |
| `sleep_duration` | 1.0–1.5 h below baseline median | `sleep_restriction` |
| `hrv_rmssd` | below median by ≥1 std **or** ≥25% | `reduced_hrv_relative_to_baseline` |
| `resting_heart_rate` | above median by ≥1 std **or** ≥15% | `elevated_heart_rate_relative_to_baseline` |
| `eda` | above median by ≥1 std **or** ≥30% | `increased_eda` |
| `salivary_cortisol` | above median by ≥1 std (if baseline exists) | `salivary_cortisol_increase` |
| `salivary_cortisol` | no baseline; only if `context.above_reference_range=true` | `salivary_cortisol_increase` |
| `illness_symptoms=true` | context only | `illness_symptoms_present` |
| `recent_exercise=true` | context only | `recent_exercise_context` |

**Confidence:** `min(1.0, observation_quality × baseline_quality_modifier × deviation_modifier)`

- Baseline quality: sample_count ≥21 → 1.0; 7–20 → 0.75; &lt;7 → 0.5; missing → 0.3
- Deviation strength: strong → 1.0; moderate → 0.75; weak → 0.5

Context-only markers (`illness_symptoms_present`, `recent_exercise_context`) are recorded in the personal graph but **excluded from inference input**.

### Build personal graph

```bash
python3 scripts/build_personal_evidence_graph.py \
  --raw data/demo_raw_observations_v0_1.json \
  --baseline data/demo_personal_baseline_v0_1.json \
  --static-graph data/static_scientific_evidence_graph_v0_1.json \
  --output outputs/demo_personal_evidence_graph_v0_1.json \
  --inference-input outputs/demo_inference_input_from_personal_graph_v0_1.json
```

### Run inference from personal graph

```bash
python3 scripts/run_inference.py \
  --graph data/static_scientific_evidence_graph_v0_1.json \
  --observations outputs/demo_inference_input_from_personal_graph_v0_1.json \
  --max-depth 4 \
  --output-json outputs/demo_personal_inference_result_v0_1.json \
  --output-md outputs/demo_personal_inference_report_v0_1.md \
  --inference-id demo_personal_inference_v0_1
```

Validate personal graph artifacts:

```bash
python3 scripts/validate_personal_evidence_graph.py \
  --personal-graph outputs/demo_personal_evidence_graph_v0_1.json \
  --inference-input outputs/demo_inference_input_from_personal_graph_v0_1.json \
  --static-nodes data/static_nodes_v0_1.json
```

### Demo expected mappings

- sleep_duration 4.5 h vs baseline 7.4 h → `sleep_loss`
- hrv_rmssd 28 ms vs baseline 48 ms → `reduced_hrv_relative_to_baseline`
- eda 2.3 vs baseline 1.2 → `increased_eda`

### Warnings

- **This is not a medical diagnosis.** Mapping rules are preliminary and conservative.
- Raw observations are **not** mapped directly to psychological states; inference always goes through static graph nodes.
- Baseline quality (`sample_count`) affects confidence scores.
- Additional context (illness, exercise, environment) may change interpretation.

## Scripts (registry and edges)

Additional registry/edge schema validation:

```bash
python3 scripts/validate_registry.py
python3 scripts/export_edges.py --help
```

## Stage and scope

v0.1 is a **static** evidence graph: curated edges and sources, not live wearable inference. It does not encode individual-level diagnostic rules and must not be read as biomarker → diagnosis mapping.
