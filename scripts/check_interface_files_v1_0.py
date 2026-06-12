#!/usr/bin/env python3
"""Static smoke test for the THSI research-grade dashboard (interface/).

Validates (each logged, failures never hidden):
  - interface/index.html, interface/styles.css, interface/app.js exist.
  - index.html references styles.css and app.js.
  - app.js references integrated_evidence_graph_v1_0.json.
  - no external CDN links (http(s):// in href/src/import).
  - no remote assets (no absolute http(s) asset URLs).
  - all required workflow / secondary tabs exist (exact labels).
  - expanded data-intake fields exist (>= 42 fields across 5 sections).
  - "Fill random demo data" button exists.
  - activated graph container exists (id="activated-graph").
  - all ten report sections exist.
  - forbidden diagnosis language is absent ("you have", "confirmed disease",
    "diagnosis confirmed", "definitive diagnosis", "confirmed diagnosis").
  - mandatory safety line "This is not a diagnosis." exists.

Writes:
  - outputs/validation/interface_smoke_test_v1_0.json
  - outputs/validation/interface_smoke_test_v1_0.md
"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTERFACE_DIR = PROJECT_ROOT / "interface"
VALIDATION_DIR = PROJECT_ROOT / "outputs" / "validation"

INDEX = INTERFACE_DIR / "index.html"
STYLES = INTERFACE_DIR / "styles.css"
APP = INTERFACE_DIR / "app.js"

REQUIRED_TABS = [
    "Workflow", "Evidence Map", "Hidden States", "Parameters",
    "Guardrails", "Corpus / Coverage", "Source Traceability",
]

DIAGNOSIS_PHRASES = [
    "you have", "confirmed disease", "diagnosis confirmed", "definitive diagnosis",
    "confirmed diagnosis",
]

# Representative expanded-intake field labels that must be present (Part 2).
REQUIRED_INTAKE_LABELS = [
    "Resting heart rate deviation", "HRV deviation", "Sleep fragmentation / WASO",
    "Respiratory rate", "Anxiety-like arousal", "Sedative / opioid / tramadol exposure",
    "High CO2 / poor ventilation", "Hemoglobin / ferritin / TSAT", "Saliva cortisol rhythm",
    "Orthostatic HR / BP", "PVT / reaction time", "CPET / exercise response",
    "Grip strength / functional mobility", "PSG / EEG sleep architecture",
]
MIN_INTAKE_FIELDS = 42
MIN_DEMO_PROFILES = 7

# The ten required report sections (Part 5).
REQUIRED_REPORT_SECTIONS = [
    "Plain-language summary", "Top candidate hidden states", "Evidence cards",
    "Activated graph", "What this does NOT prove", "Missing data",
    "Next best measurements", "Guardrails applied", "Traceable chains",
    "Source traceability",
]

MANDATORY_SAFETY_LINE = "This is not a diagnosis."

# Allowlisted non-remote schemes / safe attribute values.
SAFE_URL_PREFIXES = ("styles.css", "app.js", "#", "./", "../", "/")

logger = logging.getLogger("check_interface_files")


def configure_logging() -> None:
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S"))
    logger.addHandler(handler)


class Report:
    def __init__(self) -> None:
        self.checks: list[dict] = []

    def add(self, check_id: str, passed: bool, message: str, details=None) -> None:
        status = "PASS" if passed else "FAIL"
        self.checks.append({"check": check_id, "status": status, "passed": passed,
                            "message": message, "details": details or {}})
        (logger.info if passed else logger.error)("[%s] %s — %s", status, check_id, message)

    @property
    def all_passed(self) -> bool:
        return all(c["passed"] for c in self.checks)


def read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.error("Could not read %s: %s", path, exc)
        return None


def main() -> int:
    configure_logging()
    logger.info("=== Dashboard smoke test (interface/) ===")
    report = Report()

    report.add("index_exists", INDEX.exists(), f"index.html exists: {INDEX.exists()}")
    report.add("styles_exists", STYLES.exists(), f"styles.css exists: {STYLES.exists()}")
    report.add("app_exists", APP.exists(), f"app.js exists: {APP.exists()}")

    index_src = read(INDEX) or ""
    styles_src = read(STYLES) or ""
    app_src = read(APP) or ""

    report.add("index_references_styles", "styles.css" in index_src,
               "index.html references styles.css")
    report.add("index_references_app", "app.js" in index_src,
               "index.html references app.js")
    report.add("app_references_graph",
               "integrated_evidence_graph_v1_0.json" in app_src,
               "app.js references integrated_evidence_graph_v1_0.json")

    # No external CDN / remote assets: scan href/src/url/import for http(s).
    combined = index_src + "\n" + styles_src + "\n" + app_src
    remote = re.findall(r'(?:href|src)\s*=\s*["\']\s*(https?://[^"\']+)', combined, re.I)
    remote += re.findall(r'url\(\s*["\']?\s*(https?://[^)"\']+)', combined, re.I)
    remote += re.findall(r'@import\s+["\']\s*(https?://[^"\']+)', combined, re.I)
    remote += re.findall(r'(?:from|import)\s+["\']\s*(https?://[^"\']+)', combined, re.I)
    report.add("no_external_cdn_links", not remote,
               f"{len(remote)} external CDN/remote references found",
               {"references": remote[:20]})

    # No remote assets generally (catch fonts.googleapis, cdn., etc.).
    remote_hosts = re.findall(r'https?://[^\s"\'()<>]+', combined)
    # Exclusions that are NOT fetched assets:
    #  - the error panel instructs the user to open localhost (guidance text);
    #  - W3C XML namespace URIs (e.g. http://www.w3.org/2000/svg) are namespace
    #    identifiers required for inline SVG, never network requests.
    remote_hosts = [h for h in remote_hosts
                    if "localhost" not in h and "127.0.0.1" not in h
                    and not h.startswith("http://www.w3.org/")
                    and not h.startswith("https://www.w3.org/")]
    report.add("no_remote_assets", not remote_hosts,
               f"{len(remote_hosts)} remote asset URLs found",
               {"urls": remote_hosts[:20]})

    # No diagnosis language anywhere in the interface.
    lowered = combined.lower()
    diag_hits = [p for p in DIAGNOSIS_PHRASES if p in lowered]
    report.add("no_diagnosis_language", not diag_hits,
               f"{len(diag_hits)} diagnosis phrases found",
               {"phrases": diag_hits})

    # All required tabs exist with exact labels.
    tab_labels = re.findall(r'data-tab="[^"]+"\s+role="tab">([^<]+)</button>', index_src)
    tab_labels = [t.strip() for t in tab_labels]
    missing_tabs = [t for t in REQUIRED_TABS if t not in tab_labels]
    report.add("all_required_tabs_present", not missing_tabs,
               f"{len(REQUIRED_TABS) - len(missing_tabs)}/{len(REQUIRED_TABS)} required tabs present",
               {"found": tab_labels, "missing": missing_tabs})

    # Expanded intake fields exist: count `key:` entries in app.js and check labels.
    intake_field_count = len(re.findall(r'\bkey:\s*"', app_src))
    missing_labels = [lbl for lbl in REQUIRED_INTAKE_LABELS if lbl not in app_src]
    intake_ok = intake_field_count >= MIN_INTAKE_FIELDS and not missing_labels
    report.add("expanded_intake_fields_present", intake_ok,
               f"{intake_field_count} intake fields (need >= {MIN_INTAKE_FIELDS}); "
               f"{len(REQUIRED_INTAKE_LABELS) - len(missing_labels)}/{len(REQUIRED_INTAKE_LABELS)} representative labels present",
               {"field_count": intake_field_count, "missing_labels": missing_labels})

    # Random demo data button + >= 7 demo profiles.
    has_demo_btn = "Fill random demo data" in index_src
    demo_profile_count = len(re.findall(r'\bname:\s*"', app_src))
    report.add("random_demo_data_present",
               has_demo_btn and demo_profile_count >= MIN_DEMO_PROFILES,
               f"random-demo button present={has_demo_btn}; {demo_profile_count} demo profiles (need >= {MIN_DEMO_PROFILES})",
               {"button": has_demo_btn, "demo_profiles": demo_profile_count})

    # Activated graph container exists.
    has_graph_container = 'id="activated-graph"' in index_src
    report.add("activated_graph_container_present", has_graph_container,
               'activated graph container (id="activated-graph") present')

    # All ten report sections exist (defined in app.js).
    missing_sections = [s for s in REQUIRED_REPORT_SECTIONS if s not in app_src]
    report.add("report_sections_present", not missing_sections,
               f"{len(REQUIRED_REPORT_SECTIONS) - len(missing_sections)}/{len(REQUIRED_REPORT_SECTIONS)} report sections present",
               {"missing": missing_sections})

    # Mandatory safety line present.
    report.add("mandatory_safety_line_present", MANDATORY_SAFETY_LINE in combined,
               f'mandatory safety line "{MANDATORY_SAFETY_LINE}" present')

    # Fetch-failure guidance present (graceful offline message).
    has_guidance = ("python -m http.server 8000" in index_src
                    and "http://localhost:8000/interface/" in index_src)
    report.add("fetch_failure_guidance_present", has_guidance,
               "fetch-failure guidance (server command + URL) present")

    summary = {
        "checks_total": len(report.checks),
        "checks_passed": sum(1 for c in report.checks if c["passed"]),
        "checks_failed": sum(1 for c in report.checks if not c["passed"]),
        "tabs_found": tab_labels,
        "overall_status": "PASS" if report.all_passed else "FAIL",
    }
    _write_outputs(report, summary)
    logger.info("=== Smoke test %s (%d/%d checks passed) ===",
                summary["overall_status"], summary["checks_passed"], summary["checks_total"])
    return 0 if report.all_passed else 1


def _write_outputs(report: Report, summary: dict) -> None:
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    doc = {
        "validator": "check_interface_files_v1_0",
        "timestamp": timestamp,
        "overall_status": summary["overall_status"],
        "summary": summary,
        "checks": report.checks,
    }
    out_json = VALIDATION_DIR / "interface_smoke_test_v1_0.json"
    out_json.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Dashboard Smoke Test (interface/) — v1.0",
        "",
        f"- Validator: `check_interface_files_v1_0`",
        f"- Timestamp: {timestamp}",
        f"- Overall status: **{summary['overall_status']}**",
        f"- Checks passed: {summary['checks_passed']}/{summary['checks_total']}",
        "",
        "## Tabs found",
        "",
        "".join(f"- {t}\n" for t in summary["tabs_found"]) or "- (none)\n",
        "## Checks",
        "",
        "| Check | Status | Message |",
        "|---|---|---|",
    ]
    for c in report.checks:
        lines.append(f"| {c['check']} | {c['status']} | {c['message']} |")
    lines.append("")
    lines.append("## Failing check details")
    lines.append("")
    any_fail = False
    for c in report.checks:
        if not c["passed"] and c["details"]:
            any_fail = True
            lines.append(f"### {c['check']}")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(c["details"], indent=2, ensure_ascii=False))
            lines.append("```")
            lines.append("")
    if not any_fail:
        lines.append("None.")
    out_md = VALIDATION_DIR / "interface_smoke_test_v1_0.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", out_json.relative_to(PROJECT_ROOT))
    logger.info("Wrote %s", out_md.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    sys.exit(main())
