#!/usr/bin/env python3
"""
Run every BodyState Mapper / THSI validator as a subprocess, in a deterministic order,
and print a compact summary table.

- Each validator runs with the current Python interpreter.
- stdout and stderr are captured; on failure the tail is shown.
- A validator file that does not exist is SKIPPED with a clear note (not a failure).
- Returns exit code 0 only if every validator that ran passed.

Works both from the project root and from inside scripts/.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent

# (label, script filename, extra args). Deterministic order.
VALIDATORS: list[tuple[str, str, list[str]]] = [
    ("registry", "validate_registry.py", []),
    ("static_graph", "validate_static_graph.py", []),
    ("integrated_evidence_graph", "validate_integrated_evidence_graph_v1_0.py", []),
    ("personal_evidence_graph", "validate_personal_evidence_graph.py", []),
    ("inference_output", "validate_inference_output.py", []),
    ("personal_inference_output", "validate_personal_inference_output.py", []),
    ("inference_chains_sync", "sync_inference_chains_v1_0.py", ["--check"]),
    ("astronaut_mapping_package", "validate_astronaut_mapping_package_v1_0.py", []),
    ("source_claim_registry", "validate_source_claim_registry_v1_0.py", []),
    ("semantic_integrity", "validate_semantic_integrity_v1_0.py", []),
    ("interface_smoke_test", "check_interface_files_v1_0.py", []),
]


def run_one(label: str, script: str, extra: list[str]) -> dict:
    path = SCRIPTS_DIR / script
    if not path.is_file():
        print(f"\n=== {label}: SKIP (not found: {script}) ===")
        return {"label": label, "script": script, "status": "SKIP", "code": None,
                "seconds": 0.0}

    print(f"\n=== {label}: running {script} {' '.join(extra)} ===")
    start = time.monotonic()
    proc = subprocess.run(
        [sys.executable, str(path), *extra],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    elapsed = time.monotonic() - start
    if proc.stdout:
        print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n")
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-25:]
        if tail:
            print("--- stderr (tail) ---")
            print("\n".join(tail))
    status = "PASS" if proc.returncode == 0 else "FAIL"
    return {"label": label, "script": script, "status": status,
            "code": proc.returncode, "seconds": elapsed}


def main() -> int:
    print("=" * 70)
    print("BodyState Mapper / THSI — run_all_validations")
    print(f"Project root: {PROJECT_ROOT}")
    print("=" * 70)

    results = [run_one(label, script, extra) for label, script, extra in VALIDATORS]

    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    width = max(len(r["label"]) for r in results)
    for r in results:
        secs = f"{r['seconds']:.2f}s" if r["status"] != "SKIP" else "-"
        print(f"  {r['label']:<{width}}  {r['status']:<5}  {secs}")
    print("=" * 70)

    ran = [r for r in results if r["status"] != "SKIP"]
    passed = [r for r in ran if r["status"] == "PASS"]
    skipped = [r for r in results if r["status"] == "SKIP"]
    failed = [r for r in ran if r["status"] == "FAIL"]
    print(f"Ran: {len(ran)}  Passed: {len(passed)}  Failed: {len(failed)}  "
          f"Skipped: {len(skipped)}")
    if skipped:
        print("Skipped (not present): " + ", ".join(r["script"] for r in skipped))
    if failed:
        print("FAILED: " + ", ".join(r["label"] for r in failed))
        return 1
    print("All validators that ran PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
