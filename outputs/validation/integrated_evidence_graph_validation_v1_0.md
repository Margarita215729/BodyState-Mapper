# Integrated Evidence Graph v1.0 — Validation Report

- Validator: `validate_integrated_evidence_graph_v1_0`
- Timestamp: 2026-06-12T20:32:50.747116+00:00
- Overall status: **PASS**

## Summary

- Nodes: 1979
- Edges: 5698
- Hidden states: 54
- Guardrails: 194
- Checks passed: 15/15

## Checks

| Check | Status | Message |
|---|---|---|
| L1_parse_graph | PASS | Parsed integrated_evidence_graph_v1_0.json |
| L1_parse_nodes | PASS | Parsed integrated_evidence_graph_nodes_v1_0.json |
| L1_parse_edges | PASS | Parsed integrated_evidence_graph_edges_v1_0.json |
| L1_parse_stats | PASS | Parsed integrated_evidence_graph_stats_v1_0.json |
| edge_endpoints_exist | PASS | 0 edge endpoints missing |
| no_duplicate_node_ids | PASS | 0 duplicate node ids |
| no_duplicate_edge_ids | PASS | 0 duplicate edge ids |
| required_hidden_states_present | PASS | 33/33 required hidden states present |
| required_guardrails_present | PASS | 23/23 required guardrails present |
| elevated_hr_node_present | PASS | elevated_heart_rate_relative_to_baseline present |
| hidden_state_support_coverage | PASS | 0 ready hidden states without incoming support edge |
| measured_parameter_traceability | PASS | 0 measured parameters without source traceability |
| no_diagnosis_language_in_edges | PASS | 0 edges contain diagnosis language |
| stats_consistent | PASS | 0 stats inconsistencies |
| standalone_files_match_graph | PASS | standalone node/edge files match embedded graph |

## Failing check details

None.
