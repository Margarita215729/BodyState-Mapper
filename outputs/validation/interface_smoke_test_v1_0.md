# Dashboard Smoke Test (interface/) — v1.0

- Validator: `check_interface_files_v1_0`
- Timestamp: 2026-06-12T20:32:52.448644+00:00
- Overall status: **PASS**
- Checks passed: 19/19

## Tabs found

- Workflow
- Evidence Map
- Hidden States
- Parameters
- Guardrails
- Corpus / Coverage
- Source Traceability

## Checks

| Check | Status | Message |
|---|---|---|
| index_exists | PASS | index.html exists: True |
| styles_exists | PASS | styles.css exists: True |
| app_exists | PASS | app.js exists: True |
| index_references_styles | PASS | index.html references styles.css |
| index_references_app | PASS | index.html references app.js |
| app_references_graph | PASS | app.js references integrated_evidence_graph_v1_0.json |
| no_external_cdn_links | PASS | 0 external CDN/remote references found |
| no_remote_assets | PASS | 0 remote asset URLs found |
| no_diagnosis_language | PASS | 0 diagnosis phrases found |
| all_required_tabs_present | PASS | 7/7 required tabs present |
| expanded_intake_fields_present | PASS | 42 intake fields (need >= 42); 14/14 representative labels present |
| random_demo_data_present | PASS | random-demo button present=True; 7 demo profiles (need >= 7) |
| activated_graph_container_present | PASS | activated graph container (id="activated-graph") present |
| report_sections_present | PASS | 10/10 report sections present |
| mandatory_safety_line_present | PASS | mandatory safety line "This is not a diagnosis." present |
| fetch_failure_guidance_present | PASS | fetch-failure guidance (server command + URL) present |
| referenced_json_files_exist | PASS | 1/1 referenced JSON files exist on disk |
| no_broken_absolute_paths | PASS | 0 absolute local path reference(s) found |
| required_output_present | PASS | integrated_evidence_graph_v1_0.json present: True |

## Failing check details

None.