# Integrated Evidence Graph & Local Research Dashboard — Build Report v1.0

- **Project:** BodyState Mapper / THSI (Traceable Human State Inference Under Partial Biological Observability)
- **Extension:** Astronaut Data Mapping
- **Graph id / version:** `thsi_integrated_evidence_graph_v1_0` / 1.0
- **Build timestamp (graph):** 2026-06-11T23:21:21.655609+00:00
- **Report generated:** 2026-06-11T23:30:22.499444+00:00
- **Synthesis status:** assembled_from_existing_sources (assembled from existing project sources only)
- **Core rule:** Not a diagnostic system. Outputs are traceable hidden-state hypotheses with uncertainty, missing-data notes, guardrails, and next-best measurements. Never a diagnosis.

## Files created

**Part 1 — Integrated evidence graph**
- `outputs/astronaut_data_mapping_v1_0/integrated_evidence_graph_v1_0.json`
- `outputs/astronaut_data_mapping_v1_0/integrated_evidence_graph_nodes_v1_0.json`
- `outputs/astronaut_data_mapping_v1_0/integrated_evidence_graph_edges_v1_0.json`
- `outputs/astronaut_data_mapping_v1_0/integrated_evidence_graph_stats_v1_0.json`
- `scripts/build_integrated_evidence_graph_v1_0.py` (generator)

**Part 2 — Graph validator**
- `scripts/validate_integrated_evidence_graph_v1_0.py`
- `outputs/validation/integrated_evidence_graph_validation_v1_0.json`
- `outputs/validation/integrated_evidence_graph_validation_v1_0.md`

**Part 3 — Local research dashboard**
- `interface/index.html`
- `interface/styles.css`
- `interface/app.js`

**Part 4 — Dashboard smoke test**
- `scripts/check_interface_files_v1_0.py`
- `outputs/validation/interface_smoke_test_v1_0.json`
- `outputs/validation/interface_smoke_test_v1_0.md`

**Part 6 — This report**
- `outputs/reports/integrated_graph_and_dashboard_build_report_v1_0.md`

## Files modified

- Dashboard research-grade upgrade: `interface/index.html`, `interface/styles.css`, `interface/app.js`, and `scripts/check_interface_files_v1_0.py`. A node-color rendering bug was fixed in `interface/app.js` (SVG `fill` set with literal hex values instead of unresolved CSS `var()`).
- No source data or evidence was deleted or rewritten. The graph build still reads existing project artifacts (static graph, v1.0 package files, cleaned data inventory) and writes only the generated graph/validation/report files listed above; scientific claims and evidence were not altered.

## Graph statistics

- **Nodes:** 1979
- **Edges:** 5698
- **Hidden states:** 54 (33 required astronaut hidden states + supplementary static-graph mechanism nodes)
- **Measured parameters:** 498
- **Guardrails:** 194 (23 required present)
- **Source trees:** 93
- **Needs-review nodes:** 0; partial nodes: 413
- **High-confidence edges:** 2726; low-confidence edges: 35

### Nodes by type

| Type | Count |
|---|---|
| measured_parameter | 498 |
| required_measurement | 465 |
| inference_chain | 245 |
| context | 236 |
| guardrail | 194 |
| source_file | 93 |
| source_tree | 93 |
| result_variation | 63 |
| hidden_state | 54 |
| evidence_source | 15 |
| observation_input_type | 14 |
| response_type | 6 |
| data_quality_flag | 3 |

### Edges by type

| Type | Count |
|---|---|
| SUPPORTED_BY_SOURCE | 1621 |
| NEEDS_REVIEW | 872 |
| DERIVED_FROM | 771 |
| RECOMMENDS_MEASUREMENT | 626 |
| MEASURES | 524 |
| CAN_ACCEPT_INPUT | 431 |
| REQUIRES_CONTEXT | 328 |
| CONSTRAINED_BY_GUARDRAIL | 194 |
| CONTAINS | 155 |
| HAS_VARIATION | 63 |
| SUPPORTS_HIDDEN_STATE | 53 |
| CAN_OUTPUT_RESPONSE | 37 |
| PART_OF_CHAIN | 22 |
| CONTEXT_OVERRIDES | 1 |

## Validation results

| Validator | Status | Output |
|---|---|---|
| Integrated evidence graph validation | **PASS** | `outputs/validation/integrated_evidence_graph_validation_v1_0.json` |
| Dashboard smoke test | **PASS** | `outputs/validation/interface_smoke_test_v1_0.json` |
| Astronaut mapping package validation | **PASS** | `outputs/validation/astronaut_mapping_package_validation_v1_0.json` |
| Static scientific graph | **PASSED** | `scripts/validate_static_graph.py` (no JSON artifact; console-only) |
| Personal evidence graph | **PASSED** | `scripts/validate_personal_evidence_graph.py` (no JSON artifact; console-only) |
| Inference output | **PASSED** | `scripts/validate_inference_output.py` (no JSON artifact; console-only) |

All graph-validator checks (15/15) and dashboard smoke-test checks (16/16) passed: edge endpoints resolve, no duplicate ids, all required hidden states and guardrails present, `elevated_heart_rate_relative_to_baseline` present, every ready hidden state has an incoming support edge, every measured parameter is source-traceable, no diagnosis language in edges, and stats are consistent with the actual graph.

## Dashboard — research-grade upgrade (v1.0)

The developer/debug dashboard was rebuilt into a research-grade interactive application. No source data was deleted or rewritten; only `interface/index.html`, `interface/styles.css`, `interface/app.js`, and `scripts/check_interface_files_v1_0.py` were changed.

- **Path:** `interface/index.html`
- **Tabs:** Workflow (landing), Evidence Map, Hidden States, Parameters, Guardrails, Corpus / Coverage, Source Traceability
- **Stack:** plain HTML/CSS/JS only — no React, no npm, no backend, no external CDN, no remote assets, no external fonts. Inline SVG only for the activated graph (no graph libraries).

### What changed

- **Workflow-first landing page** — the page opens on the five-step workflow: 1 Data Intake → 2 Generate Traceable Report → 3 Activated Evidence Graph → 4 Next Measurements → 5 Source Traceability, with a persistent "Not a diagnostic system — traceable hypotheses only" safety line and `Generate report` / `Fill random demo data` / `Clear` actions.
- **Expanded data intake (42 fields, 5 collapsible sections):** A Wearable/physiology (8), B Symptoms (9), C Context (11), D Labs/biofluids (8), E Functional/objective (6). `Fill random demo data` draws coherent rule-based profiles from 7 templates (low recovery, orthostatic/dehydration, pain–sleep–fatigue, medication override, inflammatory-load, migraine, sparse missing-data).
- **Transparent client-side inference engine (21 candidate rules):** maps inputs to real graph parameter nodes where possible and emits, per candidate, `state_id`, `confidence`, `score`, `supporting_signals`, `missing_data`, `guardrails`, `activated_paths`, `not_proven`, and `next_measurements`. Confidence governance defaults to insufficient/low/moderate; `high` is reachable only with ≥3 supporting domains plus required context plus objective (labs/functional) support, and symptoms-only or single-marker support can never exceed low. Verified at runtime: across all 7 demo profiles plus empty and a high-pressure multi-domain case, no candidate was promoted past `moderate`.
- **Activated interactive graph (Part 4):** vanilla-SVG layered layout (inputs → parameters/variations → chains/context → hidden states → guardrails/measurements, with a sources band), node/edge click-to-inspect side panel, controls (active-path-only, first-degree neighbors, guardrails, required measurements, source traceability, zoom, pan, reset), and the full start→end chain rendered (e.g. *Resting heart rate increased → Elevated Heart Rate Relative To Baseline → Low Recovery State → constrained by single_marker_never_equals_mechanism → recommends measurements*). Node colors are set with literal hex values because CSS `var()` does not resolve inside SVG `fill` presentation attributes.
- **Report UI (Part 5):** ten sections — Plain-language summary, Top candidate hidden states, Evidence cards, Activated graph, What this does NOT prove, Missing data, Next best measurements, Guardrails applied, Traceable chains, Source traceability — readable for non-developers with expandable technical detail and no raw-JSON output.
- **Corpus/Coverage, Evidence Map, Hidden States, Parameters, Guardrails, Source Traceability** tabs rebuilt with CSS/vanilla-JS bar visuals, path-centric cards, readiness badges, plain-language guardrail explanations, and source-tree search.
- **Performance:** the ~6 MB graph is fetched once and indexed by id/type with incoming/outgoing adjacency maps; the SVG renders only the curated activated subgraph (tens of nodes), never all 1,979.

### Runtime verification

Validated live via a local server and an automated browser harness:

- App boots and indexes 1,979 nodes / 5,698 edges; intake renders 42 fields; Corpus, Guardrails (194 cards), Hidden States (54 cards), and Source Traceability (186 rows) populate.
- `Generate report` produces all 10 report sections, candidate cards, the activated SVG subgraph, ranked measurements, and report-scoped sources across every demo profile.
- Graph node/edge clicks open the detail side panel; node fills render in the correct layer colors.
- No forbidden diagnosis language ("you have", "confirmed disease", "diagnosis confirmed", "definitive diagnosis", "confirmed diagnosis") appears in rendered output; the mandatory line "This is not a diagnosis." is present.

> Note on caching: the dashboard references `app.js` without a version query, so after upgrading, a hard refresh (or disabling cache) is required to pick up the new script if a previous version was already loaded in the browser.

### How to open the dashboard

```bash
cd "/Users/rm/Desktop/BodyState Mapper"
python3 -m http.server 8000
# then open:
# http://localhost:8000/interface/
```

The dashboard loads `../outputs/astronaut_data_mapping_v1_0/integrated_evidence_graph_v1_0.json`. If opened via `file://` the fetch fails and the page shows the server command and URL above.

## Known limitations

- The graph is **assembled from existing sources** (no new evidence generated). Synthesized/weak links are marked low confidence; cross-type links inferred by keyword (e.g. input-category → parameter) are moderate confidence.
- 19 of 34 astronaut hidden states are `partial` (no standalone supporting chain in the source package); they are exempt from the support-edge requirement and flagged for review. Static scientific-graph mechanism nodes are imported as supplementary `partial` hidden-state bridges.
- The Traceable Inference Demo is an intentionally transparent rule engine, not ML, and is illustrative only.
- Guardrail→hidden-state bindings combine the contract's universal guardrails with definitional domain bindings; they express constraint relationships, not statistical associations.

## Next recommended step

- Promote `partial` hidden states to `ready` by curating explicit supporting chains and source files for them in the package, then rebuild; this will add SUPPORTS_HIDDEN_STATE coverage and reduce the review backlog. Re-run `scripts/validate_integrated_evidence_graph_v1_0.py` after any change.
