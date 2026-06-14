#!/usr/bin/env python3
"""
BodyState Mapper v1.0 Package Validator
Validates all package artifacts for correctness and completeness.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _project_paths import PROJECT_ROOT, DATA_DIR, OUTPUTS_DIR

PKG_DIR = OUTPUTS_DIR / "astronaut_data_mapping_v1_0"
VALIDATION_DIR = OUTPUTS_DIR / "validation"

EXPECTED_FILES = [
    "astronaut_data_sources_v1_0.json",
    "measured_entities_v1_0.json",
    "measured_parameter_registry_v1_0.json",
    "result_variation_trees_v1_0.json",
    "cross_modal_links_v1_0.json",
    "hidden_state_candidates_v1_0.json",
    "inference_chains_v1_0.json",
    "guardrails_v1_0.json",
    "required_measurements_v1_0.json",
    "mission_phase_interpretation_v1_0.json",
    "all_to_all_matrix_v1_0.json",
    "validation_protocol_v1_0.json",
    "data_intake_contract_v1_0.json",
    "README.md",
]

REQUIRED_GUARDRAILS = [
    "unknown_is_not_negative_evidence",
    "single_marker_never_equals_mechanism",
    "medication_timing_first",
]

REQUIRED_HIDDEN_STATES = [
    "low_recovery_state", "acute_sleep_loss", "orthostatic_intolerance",
    "PEM_objective_branch", "unknown_or_missing_data_state",
]

REQUIRED_REGISTRY_FIELDS = [
    "parameter_id", "display_name", "source_files", "evidence_strength", "pipeline_status"
]

REQUIRED_HIDDEN_STATE_FIELDS = [
    "hidden_state_id", "display_name", "confidence", "pipeline_status", "not_a_diagnosis"
]

REQUIRED_CHAIN_FIELDS = [
    "chain_id", "chain", "confidence", "source_file"
]

REQUIRED_GUARDRAIL_FIELDS = [
    "guardrail_id", "text"
]

REQUIRED_MATRIX_FIELDS = ["source", "target"]

REQUIRED_INTAKE_SECTIONS = [
    "accepted_source_categories", "universal_observation_object_schema",
    "wearable_intake_fields", "self_report_intake_fields", "clinical_lab_intake_fields",
    "context_intake_fields", "allowed_result_variation_categories",
    "interpretation_levels", "confidence_levels", "response_types",
    "required_guardrails_in_output", "minimal_mvp_intake_form", "minimal_mvp_output_form",
]

TARGET_NODE = "elevated_heart_rate_relative_to_baseline"
R001_ALIAS = "astro_data_tree_R001_blood_systemic_CBC_CMP_electrolytes_kidney_liver_repair.cleaned.json"
R002_CANONICAL = "astro_data_tree_002_blood_systemic_CBC_CMP_electrolytes_kidney_liver_repair.cleaned.json"


class Validator:
    def __init__(self):
        self.failures = []
        self.warnings = []
        self.passes = []
        self.ts = datetime.now(timezone.utc).isoformat()

    def fail(self, check_id, msg):
        print(f"  [FAIL] {check_id}: {msg}")
        self.failures.append({"check_id": check_id, "message": msg})

    def warn(self, check_id, msg):
        print(f"  [WARN] {check_id}: {msg}")
        self.warnings.append({"check_id": check_id, "message": msg})

    def ok(self, check_id, msg=""):
        print(f"  [PASS] {check_id}" + (f": {msg}" if msg else ""))
        self.passes.append({"check_id": check_id, "message": msg})

    def load(self, filename):
        path = PKG_DIR / filename
        if not path.is_file():
            self.fail(f"file_exists_{filename[:30]}", f"File not found: {filename}")
            return None
        try:
            with open(path) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.fail(f"json_parse_{filename[:30]}", f"JSON parse error in {filename}: {e}")
            return None

    def run(self):
        print("\n" + "="*60)
        print("BodyState Mapper v1.0 Package Validation")
        print("="*60)

        # Check 1: All expected files exist
        print("\n[CHECK 1] Expected package files...")
        all_exist = True
        loaded = {}
        for fn in EXPECTED_FILES:
            path = PKG_DIR / fn
            if path.is_file():
                self.ok(f"file_exists", fn)
                if fn.endswith(".json"):
                    data = self.load(fn)
                    if data is not None:
                        loaded[fn] = data
            else:
                self.fail(f"file_exists", f"MISSING: {fn}")
                all_exist = False

        # Check 2: JSON parse all package files
        print("\n[CHECK 2] JSON parse validation...")
        for fn, data in loaded.items():
            self.ok("json_valid", fn)

        # Check 3: Parameter registry required fields
        print("\n[CHECK 3] Parameter registry required fields...")
        reg = loaded.get("measured_parameter_registry_v1_0.json", {})
        params = reg.get("parameters", [])
        if not params:
            self.fail("registry_not_empty", "measured_parameter_registry_v1_0.json has no parameters")
        else:
            self.ok("registry_not_empty", f"{len(params)} parameters")
            missing_fields_count = 0
            for p in params[:50]:  # sample check
                for field in REQUIRED_REGISTRY_FIELDS:
                    if field not in p:
                        missing_fields_count += 1
            if missing_fields_count == 0:
                self.ok("registry_required_fields", "All required fields present in sampled entries")
            else:
                self.warn("registry_required_fields", f"{missing_fields_count} missing required fields in sample")

        # Check 4: Hidden states required fields
        print("\n[CHECK 4] Hidden state candidates required fields...")
        hs_data = loaded.get("hidden_state_candidates_v1_0.json", {})
        hs_list = hs_data.get("hidden_states", [])
        if not hs_list:
            self.fail("hidden_states_not_empty", "hidden_state_candidates_v1_0.json has no hidden states")
        else:
            self.ok("hidden_states_not_empty", f"{len(hs_list)} hidden states")
            hs_ids = {h["hidden_state_id"] for h in hs_list if "hidden_state_id" in h}
            for req_hs in REQUIRED_HIDDEN_STATES:
                if req_hs in hs_ids:
                    self.ok("required_hidden_state_present", req_hs)
                else:
                    self.warn("required_hidden_state_present", f"Not found: {req_hs}")
            bad_fields = 0
            for h in hs_list:
                for field in REQUIRED_HIDDEN_STATE_FIELDS:
                    if field not in h:
                        bad_fields += 1
            if bad_fields == 0:
                self.ok("hidden_state_required_fields", "All required fields present")
            else:
                self.warn("hidden_state_required_fields", f"{bad_fields} missing required fields")

        # Check 5: Inference chains required fields
        print("\n[CHECK 5] Inference chains required fields...")
        chains_data = loaded.get("inference_chains_v1_0.json", {})
        chains = chains_data.get("inference_chains", [])
        if not chains:
            self.fail("chains_not_empty", "inference_chains_v1_0.json has no chains")
        else:
            self.ok("chains_not_empty", f"{len(chains)} chains")
            bad = sum(1 for c in chains if not all(f in c for f in REQUIRED_CHAIN_FIELDS))
            if bad == 0:
                self.ok("chain_required_fields", "All required fields present")
            else:
                self.warn("chain_required_fields", f"{bad} chains missing required fields")

        # Check 6: Guardrails required fields
        print("\n[CHECK 6] Guardrails required fields...")
        gr_data = loaded.get("guardrails_v1_0.json", {})
        gr_list = gr_data.get("guardrails", [])
        if not gr_list:
            self.fail("guardrails_not_empty", "guardrails_v1_0.json has no guardrails")
        else:
            self.ok("guardrails_not_empty", f"{len(gr_list)} guardrails")

        # Check 7: All-to-all matrix required fields
        print("\n[CHECK 7] All-to-all matrix required fields...")
        matrix_data = loaded.get("all_to_all_matrix_v1_0.json", {})
        matrix = matrix_data.get("matrix", [])
        if not matrix:
            self.warn("matrix_not_empty", "all_to_all_matrix_v1_0.json has no matrix entries")
        else:
            self.ok("matrix_not_empty", f"{len(matrix)} entries")
            bad = sum(1 for m in matrix if not all(f in m for f in REQUIRED_MATRIX_FIELDS))
            if bad == 0:
                self.ok("matrix_required_fields", "All required fields present")
            else:
                self.warn("matrix_required_fields", f"{bad} entries missing required fields")

        # Check 8: Data intake contract sections
        print("\n[CHECK 8] Data intake contract sections...")
        dic = loaded.get("data_intake_contract_v1_0.json", {})
        if not dic:
            self.fail("intake_contract_present", "data_intake_contract_v1_0.json missing or empty")
        else:
            for section in REQUIRED_INTAKE_SECTIONS:
                if section in dic:
                    self.ok("intake_section_present", section)
                else:
                    self.fail("intake_section_present", f"Missing section: {section}")

        # Check 9: unknown_is_not_negative_evidence in guardrails
        print("\n[CHECK 9] Core guardrail: unknown_is_not_negative_evidence...")
        gr_ids = {g.get("guardrail_id", "") for g in gr_list}
        gr_texts = " ".join(g.get("text", "") + g.get("guardrail_id", "") for g in gr_list)
        if "unknown_is_not_negative_evidence" in gr_ids:
            self.ok("guardrail_unknown_not_negative", "Found by ID")
        elif "unknown" in gr_texts.lower() and "negative" in gr_texts.lower():
            self.ok("guardrail_unknown_not_negative", "Found by text content")
        else:
            self.fail("guardrail_unknown_not_negative", "MISSING: unknown_is_not_negative_evidence")

        # Check 10: single_marker_never_equals_mechanism
        print("\n[CHECK 10] Core guardrail: single_marker_never_equals_mechanism...")
        if "single_marker_never_equals_mechanism" in gr_ids:
            self.ok("guardrail_single_marker", "Found by ID")
        else:
            self.fail("guardrail_single_marker", "MISSING: single_marker_never_equals_mechanism")

        # Check 11: medication_timing_first
        print("\n[CHECK 11] Core guardrail: medication_timing_first...")
        if "medication_timing_first" in gr_ids:
            self.ok("guardrail_medication_timing", "Found by ID")
        else:
            self.fail("guardrail_medication_timing", "MISSING: medication_timing_first")

        # Check 12: elevated_heart_rate_relative_to_baseline in available static node files
        print(f"\n[CHECK 12] Node {TARGET_NODE} in static node files...")
        static_files = [
            DATA_DIR / "static_nodes_v0_1.json",
            DATA_DIR / "static_scientific_evidence_graph_v0_1.json",
        ]
        out_static = OUTPUTS_DIR / "static_nodes_v0_1.json"
        if out_static.is_file():
            static_files.append(out_static)
        for sf in static_files:
            if not sf.is_file():
                self.warn("static_node_file_exists", f"Static file not found: {sf.name}")
                continue
            try:
                with open(sf) as f:
                    sdata = json.load(f)
                nodes = sdata if isinstance(sdata, list) else sdata.get("nodes", [])
                ids = [n.get("node_id", "") for n in nodes if isinstance(n, dict)]
                if TARGET_NODE in ids:
                    self.ok("elevated_hr_node_in_static_file", sf.name)
                else:
                    self.fail("elevated_hr_node_in_static_file", f"NOT FOUND in {sf.name}")
            except Exception as e:
                self.fail("elevated_hr_node_in_static_file", f"Error reading {sf.name}: {e}")

        # Check 13: R001 present or mapped to canonical 002
        print("\n[CHECK 13] R001 alias / canonical 002 mapping...")
        # Cleaned Data is at project root level
        cleaned = PROJECT_ROOT / "Cleaned Data"
        if not cleaned.is_dir():
            cleaned = DATA_DIR / "Cleaned Data"
        r001_exists = (cleaned / R001_ALIAS).is_file()
        r002_exists = (cleaned / R002_CANONICAL).is_file()
        if r001_exists or r002_exists:
            self.ok("r001_r002_present", f"R001={r001_exists}, R002={r002_exists}")
        else:
            self.fail("r001_r002_present", "Neither R001 alias nor canonical 002 found")

        inv_data = loaded.get("source_file_inventory_v1_0.json", {})
        if inv_data:
            inv_files = inv_data.get("files", [])
            r001_rec = next((f for f in inv_files if R001_ALIAS in f.get("filename", "")), None)
            if r001_rec:
                if r001_rec.get("alias_of"):
                    self.ok("r001_mapped_to_canonical", f"alias_of={r001_rec['alias_of']}")
                else:
                    self.warn("r001_mapped_to_canonical", "R001 found but alias_of not set")

        # Check 14: No invalid_superseded file as primary
        print("\n[CHECK 14] No superseded file as primary source...")
        if inv_data:
            inv_files = inv_data.get("files", [])
            superseded_primary = [f for f in inv_files if f.get("inferred_role") == "invalid_superseded" and f.get("pipeline_use_priority") == "primary"]
            if superseded_primary:
                self.fail("no_superseded_primary", f"{len(superseded_primary)} superseded files marked as primary")
            else:
                self.ok("no_superseded_primary", "No superseded files marked as primary")

        # Check 15: No duplicate alias as primary
        print("\n[CHECK 15] No duplicate alias as primary...")
        if inv_data:
            inv_files = inv_data.get("files", [])
            seen = {}
            dup_primary = []
            for f in inv_files:
                if f.get("pipeline_use_priority") == "primary":
                    gid = f.get("canonical_group_id", "")
                    if gid in seen:
                        dup_primary.append((gid, f["filename"]))
                    seen[gid] = f["filename"]
            if dup_primary:
                self.warn("no_duplicate_alias_primary", f"{len(dup_primary)} duplicate group IDs as primary: {dup_primary[:3]}")
            else:
                self.ok("no_duplicate_alias_primary", "No duplicate alias as primary")

        # Check 16: Traceability for major hidden states
        print("\n[CHECK 16] Hidden state traceability...")
        if hs_list:
            for h in hs_list:
                hid = h.get("hidden_state_id", "")
                has_source = bool(h.get("source_files") or h.get("supporting_chains"))
                is_partial = h.get("pipeline_status") in {"partial", "needs_review"} or h.get("needs_review")
                if has_source:
                    self.ok("hidden_state_traceability", f"{hid}: traceable")
                elif is_partial:
                    self.warn("hidden_state_traceability", f"{hid}: no source, marked partial/needs_review")
                else:
                    self.warn("hidden_state_traceability", f"{hid}: no source and not marked partial")

        # Check 17: No hidden state claims diagnosis
        print("\n[CHECK 17] No hidden state claims final diagnosis...")
        if hs_list:
            diag_claims = [h for h in hs_list if not h.get("not_a_diagnosis", True) or "diagnosis" in h.get("output_type", "")]
            if diag_claims:
                self.fail("no_diagnosis_claim", f"{len(diag_claims)} hidden states claim diagnosis")
            else:
                self.ok("no_diagnosis_claim", "No hidden states claim diagnosis as final conclusion")

        # Summary
        print("\n" + "="*60)
        print(f"VALIDATION COMPLETE")
        print(f"  Passes:   {len(self.passes)}")
        print(f"  Warnings: {len(self.warnings)}")
        print(f"  Failures: {len(self.failures)}")
        print("="*60)

        overall = "PASS" if not self.failures else "FAIL"
        result = {
            "validation_timestamp": self.ts,
            "overall_result": overall,
            "passes": len(self.passes),
            "warnings": len(self.warnings),
            "failures": len(self.failures),
            "pass_details": self.passes,
            "warning_details": self.warnings,
            "failure_details": self.failures,
        }

        VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
        json_path = VALIDATION_DIR / "astronaut_mapping_package_validation_v1_0.json"
        with open(json_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"[WRITE] {json_path}")

        md_lines = [
            "# Astronaut Mapping Package Validation v1.0",
            f"**Timestamp:** {self.ts}",
            f"**Overall:** {overall}",
            f"- Passes: {len(self.passes)}",
            f"- Warnings: {len(self.warnings)}",
            f"- Failures: {len(self.failures)}",
            "",
        ]
        if self.failures:
            md_lines.append("## Failures")
            for f in self.failures:
                md_lines.append(f"- **{f['check_id']}**: {f['message']}")
            md_lines.append("")
        if self.warnings:
            md_lines.append("## Warnings")
            for w in self.warnings:
                md_lines.append(f"- {w['check_id']}: {w['message']}")
            md_lines.append("")
        md_lines.append("## Passes")
        for p in self.passes:
            md_lines.append(f"- {p['check_id']}" + (f": {p['message']}" if p['message'] else ""))

        md_path = VALIDATION_DIR / "astronaut_mapping_package_validation_v1_0.md"
        with open(md_path, "w") as f:
            f.write("\n".join(md_lines))
        print(f"[WRITE] {md_path}")

        return overall == "PASS"


if __name__ == "__main__":
    v = Validator()
    ok = v.run()
    sys.exit(0 if ok else 1)
