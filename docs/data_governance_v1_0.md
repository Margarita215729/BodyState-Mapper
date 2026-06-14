# Data Governance — BodyState Mapper / THSI v1.0

Scientific name: Traceable Human State Inference Under Partial Biological Observability.
Public name: BodyState Mapper.

This document defines how data and artifacts are classified, how generated material is
promoted into the curated scientific core, and the policy against invented evidence. It
is the authoritative reference for reviewers assessing the provenance and trustworthiness
of any artifact in this repository.

This project is not a diagnostic system. All outputs are traceable, uncertainty-aware
hidden-state hypotheses, never diagnoses.

## 1. Curated scientific core

The curated scientific core is authored and human-reviewed. It is the source of truth
from which all generated artifacts are derived. It consists of:

- Evidence source registry — `data/evidence_source_registry_v0_1.json` (and the parallel
  CSV/Markdown renderings). Each entry references a source PDF present in `sources_pdf/`.
- Static scientific nodes — `data/static_nodes_v0_1.json`.
- Static scientific edges — `data/static_scientific_edges_v0_1.json`. Every edge traces
  to one or more registered source ids.
- Reviewed source metadata / source cards — the per-source fields in the registry
  (findings, limitations, risk of overinterpretation, supported nodes/edges).
- Source-claim registry — `data/source_claim_registry_v1_0.json`, which links sources to
  the curated nodes and edges they support, using claim text copied verbatim from curated
  source metadata.

Schemas governing the curated core live in `schemas/` and are enforced by the validators.

## 2. Generated / integrated outputs

Generated artifacts are produced by the build scripts and are reproducible from the
curated core. They live under `outputs/` and include:

- Integrated evidence graph — `outputs/astronaut_data_mapping_v1_0/integrated_evidence_graph_v1_0.json`
  (plus its `_nodes_`, `_edges_`, and `_stats_` renderings).
- Astronaut data-mapping package — the full set of artifacts under
  `outputs/astronaut_data_mapping_v1_0/` (measured parameter registry, hidden-state
  candidates, guardrails, required measurements, cross-modal links, result-variation
  trees, mission-phase interpretation, all-to-all matrix, data-intake contract, and the
  package README).
- Generated measurement mappings — the measured-parameter and required-measurement
  derivations from the source data trees.
- Inference chains — `inference_chains_v1_0.json`, reconstructed from the integrated
  graph's `inference_chain` nodes by `scripts/sync_inference_chains_v1_0.py`. The
  integrated graph is the single source of truth for chains.
- Interface outputs — the integrated graph consumed by the static dashboard in
  `interface/`, and validation reports under `outputs/validation/`.

Generated build reports under `outputs/reports/` are logs of build runs. They are
artifacts, not curated evidence, and may be regenerated.

## 3. Promotion rule (generated to curated)

A generated artifact (or a relationship within one) may be promoted into the curated
scientific core only after ALL of the following are satisfied and recorded:

1. Source traceability verified — the relationship traces to one or more registered
   evidence sources whose PDFs are present in `sources_pdf/`.
2. Schema validation passes — the artifact conforms to its schema in `schemas/`
   (`scripts/validate_registry.py` and the relevant graph validators succeed).
3. Semantic validation passes — `scripts/validate_semantic_integrity_v1_0.py` succeeds
   for the affected graph (endpoints resolve, no duplicates, no orphan sources, counts
   consistent).
4. Uncertainty and causal status are explicit — the relationship records its confidence,
   relationship type, and any forbidden direct inferences; uncertainty is preserved and
   not collapsed.
5. Limitations recorded — the limitations and risk-of-overinterpretation for the source
   and relationship are captured in the curated metadata.

Until all five conditions hold, the material remains a generated output and is labelled
accordingly (for example with `pipeline_status` set to a scaffold/partial state or
`needs_review`).

## 4. No-invented-evidence policy

- No scientific claim, finding, or numeric result is fabricated. Claim text in the
  source-claim registry is copied verbatim from existing curated source metadata.
- Links between sources and graph elements are derived from existing references
  (for example an edge's `source_ids`), never asserted speculatively.
- Missing data is represented explicitly as missing. It is never treated as negative
  evidence, and absence of a measurement never strengthens a hypothesis.
- When the integrated graph and an exported artifact disagree, the integrated graph is
  authoritative and the export is regenerated from it; the more conservative
  (uncertainty-preserving) value is retained.
- Source data files, schemas, scripts, outputs, PDFs, and interface files are preserved.
  Schema definitions are adjusted to match semantically richer data rather than editing
  the data to fit a narrower schema.
