#!/usr/bin/env python3
"""
Semantic integrity validator for the BodyState Mapper / THSI integrated evidence graph
and its exported package artifacts.

Checks (each reported PASS/FAIL):
  1.  Every edge endpoint (source, target) resolves to an existing node.
  2.  Every edge that carries source references (source_files) resolves to a known
      source (source_file node / evidence source), when source information is available.
  3.  Every hidden_state node has >=1 incoming evidence / mapping / inference edge,
      unless it is explicitly marked as scaffold / future / needs_review.
  4.  Every guardrail node is connected to >=1 other node (incoming or outgoing edge).
  5.  Every measured_parameter node has a measurement category / observable type, or
      verifiable measurement-source provenance.
  6.  No duplicate node ids.
  7.  No duplicate edge ids.
  8.  No orphan source references (referenced source ids/files that are not defined).
  9.  No declared count contradicts actual file content (inference chains, stats file,
      hidden-state / guardrail / measured-parameter / source-claim totals).
  10. No hardcoded absolute local home path remains in scripts, schemas, curated data,
      interface, or top-level docs (clearly-marked doc examples are exempt).

Exits 0 only if all checks pass; non-zero otherwise.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _project_paths import (  # noqa: E402
    PROJECT_ROOT,
    DATA_DIR,
    SCHEMAS_DIR,
    SCRIPTS_DIR,
    INTERFACE_DIR,
    OUTPUTS_DIR,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("validate_semantic_integrity")

PKG_DIR = OUTPUTS_DIR / "astronaut_data_mapping_v1_0"
INTEGRATED_GRAPH = PKG_DIR / "integrated_evidence_graph_v1_0.json"
INFERENCE_CHAINS = PKG_DIR / "inference_chains_v1_0.json"
STATS_FILE = PKG_DIR / "integrated_evidence_graph_stats_v1_0.json"
HIDDEN_STATES_FILE = PKG_DIR / "hidden_state_candidates_v1_0.json"
GUARDRAILS_FILE = PKG_DIR / "guardrails_v1_0.json"
MEASURED_PARAM_FILE = PKG_DIR / "measured_parameter_registry_v1_0.json"
SOURCE_CLAIM_FILE = DATA_DIR / "source_claim_registry_v1_0.json"

# Incoming edge types that count as evidence / mapping / inference support.
EVIDENCE_MAPPING_INFERENCE_EDGES = {
    "SUPPORTS_HIDDEN_STATE",
    "SUPPORTED_BY_SOURCE",
    "DERIVED_FROM",
    "PART_OF_CHAIN",
    "MEASURES",
    "RECOMMENDS_MEASUREMENT",
    "CAN_ACCEPT_INPUT",
    "CONTAINS",
    "HAS_VARIATION",
    "CONTEXT_OVERRIDES",
    "CONTRADICTS_OR_REDUCES_CONFIDENCE",
    "REQUIRES_CONTEXT",
}

# Markers that exempt a hidden_state from requiring incoming evidence edges.
SCAFFOLD_STATUSES = {"partial", "scaffold", "future", "planned", "candidate", "draft"}

# Absolute home-directory path patterns that must not appear in tracked code/data/docs.
_HOME = "/Users/"  # doc-example: pattern literal, not a real path
ABS_PATH_RE = re.compile(
    r"(" + re.escape(_HOME) + r"[^/\s\"']+"  # doc-example
    r"|/home/[^/\s\"']+"  # doc-example
    r"|[A-Za-z]:\\Users\\)"  # doc-example
)
DOC_EXAMPLE_MARKERS = ("doc-example", "<project root>", "<PROJECT_ROOT>")


class Report:
    def __init__(self) -> None:
        self.results: list[tuple[str, bool, list[str]]] = []

    def add(self, name: str, ok: bool, details: list[str] | None = None) -> None:
        self.results.append((name, ok, details or []))
        status = "PASS" if ok else "FAIL"
        logger.info("[%s] %s", status, name)
        if not ok:
            for d in (details or [])[:25]:
                logger.error("    - %s", d)
            extra = len(details or []) - 25
            if extra > 0:
                logger.error("    - ... and %d more", extra)

    @property
    def ok(self) -> bool:
        return all(ok for _, ok, _ in self.results)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check_edges_endpoints(nodes: list[dict], edges: list[dict], report: Report) -> None:
    node_ids = {n.get("id") for n in nodes}
    bad = []
    for e in edges:
        for end in ("source", "target"):
            if e.get(end) not in node_ids:
                bad.append(f"edge {e.get('id')!r}: {end}={e.get(end)!r} not a node")
    report.add("edge_endpoints_resolve", not bad, bad)


def check_edge_sources(nodes: list[dict], edges: list[dict], report: Report) -> None:
    node_ids = {n.get("id") for n in nodes}
    source_filenames = {
        n.get("label")
        for n in nodes
        if n.get("type") == "source_file" and n.get("label")
    }
    try:
        evidence_reg = load_json(DATA_DIR / "evidence_source_registry_v0_1.json")
        for s in evidence_reg:
            if s.get("pdf_filename"):
                source_filenames.add(s["pdf_filename"])
    except FileNotFoundError:
        pass

    bad = []
    for e in edges:
        for fname in e.get("source_files", []) or []:
            if fname in source_filenames or f"file::{fname}" in node_ids:
                continue
            bad.append(f"edge {e.get('id')!r}: source_file {fname!r} not a known source")
    report.add("edge_source_references_known", not bad, bad)


def check_hidden_states(nodes: list[dict], edges: list[dict], report: Report) -> None:
    incoming: dict[str, int] = {}
    for e in edges:
        if e.get("type") in EVIDENCE_MAPPING_INFERENCE_EDGES:
            incoming[e.get("target")] = incoming.get(e.get("target"), 0) + 1
    bad = []
    for n in nodes:
        if n.get("type") != "hidden_state":
            continue
        if incoming.get(n.get("id"), 0) >= 1:
            continue
        meta = n.get("metadata", {}) or {}
        exempt = (
            n.get("pipeline_status") in SCAFFOLD_STATUSES
            or meta.get("needs_review")
            or meta.get("scaffold")
            or meta.get("future")
        )
        if not exempt:
            bad.append(
                f"hidden_state {n.get('id')!r} has no incoming evidence/mapping/inference "
                f"edge and is not marked scaffold/future/needs_review "
                f"(pipeline_status={n.get('pipeline_status')!r})"
            )
    report.add("hidden_states_supported_or_scaffold", not bad, bad)


def check_guardrails(nodes: list[dict], edges: list[dict], report: Report) -> None:
    degree: dict[str, int] = {}
    for e in edges:
        degree[e.get("source")] = degree.get(e.get("source"), 0) + 1
        degree[e.get("target")] = degree.get(e.get("target"), 0) + 1
    bad = [
        f"guardrail {n.get('id')!r} is not connected to any node"
        for n in nodes
        if n.get("type") == "guardrail" and degree.get(n.get("id"), 0) == 0
    ]
    report.add("guardrails_connected", not bad, bad)


def check_measured_parameters(nodes: list[dict], report: Report) -> None:
    bad = []
    for n in nodes:
        if n.get("type") != "measured_parameter":
            continue
        meta = n.get("metadata", {}) or {}
        has_modality = bool(
            meta.get("measurement_types")
            or meta.get("sample_or_sensor")
            or meta.get("units_if_known")
            or meta.get("observable_type")
            or meta.get("static_node_type")
            or meta.get("aliases")
        )
        has_provenance = bool(n.get("source_files") or n.get("source_tree_ids"))
        if not (has_modality or has_provenance):
            bad.append(
                f"measured_parameter {n.get('id')!r} has no measurement category, "
                f"observable type, or measurement-source provenance"
            )
    report.add("measured_parameters_have_observable_type", not bad, bad)


def check_duplicates(nodes: list[dict], edges: list[dict], report: Report) -> None:
    nid: dict[str, int] = {}
    for n in nodes:
        nid[n.get("id")] = nid.get(n.get("id"), 0) + 1
    dup_nodes = sorted(k for k, v in nid.items() if v > 1)
    report.add(
        "no_duplicate_node_ids",
        not dup_nodes,
        [f"duplicate node id: {d}" for d in dup_nodes],
    )
    eid: dict[str, int] = {}
    for e in edges:
        eid[e.get("id")] = eid.get(e.get("id"), 0) + 1
    dup_edges = sorted(k for k, v in eid.items() if v > 1)
    report.add(
        "no_duplicate_edge_ids",
        not dup_edges,
        [f"duplicate edge id: {d}" for d in dup_edges],
    )


def check_orphan_sources(nodes: list[dict], edges: list[dict], report: Report) -> None:
    node_ids = {n.get("id") for n in nodes}
    source_filenames = {
        n.get("label")
        for n in nodes
        if n.get("type") == "source_file" and n.get("label")
    }
    bad = []
    for e in edges:
        if e.get("type") != "SUPPORTED_BY_SOURCE":
            continue
        tgt = e.get("target")
        if tgt in node_ids:
            continue
        bad.append(f"SUPPORTED_BY_SOURCE edge {e.get('id')!r} -> undefined source {tgt!r}")
    for e in edges:
        for fname in e.get("source_files", []) or []:
            if fname not in source_filenames and f"file::{fname}" not in node_ids:
                bad.append(
                    f"edge {e.get('id')!r}: orphan source_file reference {fname!r}"
                )
    report.add("no_orphan_source_references", not bad, bad)


def check_count_claims(nodes: list[dict], edges: list[dict], report: Report) -> None:
    bad = []

    # inference chains: declared == array == graph inference_chain node count
    chain_nodes = sum(1 for n in nodes if n.get("type") == "inference_chain")
    if INFERENCE_CHAINS.is_file():
        ic = load_json(INFERENCE_CHAINS)
        arr = ic.get("inference_chains", [])
        declared = ic.get("total_chains")
        if declared != len(arr):
            bad.append(
                f"inference_chains: total_chains {declared} != array len {len(arr)}"
            )
        if len(arr) != chain_nodes:
            bad.append(
                f"inference_chains: array len {len(arr)} != graph inference_chain "
                f"nodes {chain_nodes}"
            )
        if declared and not arr:
            bad.append("inference_chains: total claims nonzero but array is empty")

    # stats file vs actual graph
    if STATS_FILE.is_file():
        stats = load_json(STATS_FILE).get("stats", {})
        if stats.get("node_count") not in (None, len(nodes)):
            bad.append(
                f"stats node_count {stats.get('node_count')} != actual {len(nodes)}"
            )
        if stats.get("edge_count") not in (None, len(edges)):
            bad.append(
                f"stats edge_count {stats.get('edge_count')} != actual {len(edges)}"
            )
        actual_by_type: dict[str, int] = {}
        for n in nodes:
            actual_by_type[n.get("type")] = actual_by_type.get(n.get("type"), 0) + 1
        for t, c in (stats.get("nodes_by_type") or {}).items():
            if actual_by_type.get(t, 0) != c:
                bad.append(
                    f"stats nodes_by_type[{t}] {c} != actual {actual_by_type.get(t, 0)}"
                )

    # self-consistency of total/array pairs
    for path, total_key, arr_key in [
        (HIDDEN_STATES_FILE, "total_hidden_states", "hidden_states"),
        (GUARDRAILS_FILE, "total_guardrails", "guardrails"),
        (MEASURED_PARAM_FILE, "total_parameters", "parameters"),
    ]:
        if path.is_file():
            d = load_json(path)
            if isinstance(d, dict) and arr_key in d:
                if d.get(total_key) != len(d[arr_key]):
                    bad.append(
                        f"{path.name}: {total_key} {d.get(total_key)} != array len "
                        f"{len(d[arr_key])}"
                    )

    if SOURCE_CLAIM_FILE.is_file():
        scr = load_json(SOURCE_CLAIM_FILE)
        meta = scr.get("metadata", {})
        claims = scr.get("source_claims", [])
        if meta.get("total_sources") != len(claims):
            bad.append(
                f"source_claim_registry: total_sources {meta.get('total_sources')} != "
                f"{len(claims)}"
            )
        actual_claims = sum(len(c.get("claims", [])) for c in claims)
        if meta.get("total_claims") != actual_claims:
            bad.append(
                f"source_claim_registry: total_claims {meta.get('total_claims')} != "
                f"{actual_claims}"
            )

    report.add("count_claims_consistent", not bad, bad)


def check_no_hardcoded_paths(report: Report) -> None:
    scan_targets: list[Path] = []
    scan_targets += sorted(SCRIPTS_DIR.glob("*.py"))
    scan_targets += sorted(SCHEMAS_DIR.glob("*.json"))
    scan_targets += sorted(DATA_DIR.glob("*.json"))
    scan_targets += sorted(DATA_DIR.glob("*.csv"))
    if INTERFACE_DIR.is_dir():
        for ext in ("*.js", "*.html", "*.css"):
            scan_targets += sorted(INTERFACE_DIR.glob(ext))
    scan_targets += sorted(PROJECT_ROOT.glob("*.md"))
    scan_targets += sorted(PROJECT_ROOT.glob("*.py"))

    bad = []
    for path in scan_targets:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if any(marker in line for marker in DOC_EXAMPLE_MARKERS):
                continue
            if ABS_PATH_RE.search(line):
                rel = path.relative_to(PROJECT_ROOT)
                bad.append(f"{rel}:{lineno}: hardcoded absolute path: {line.strip()[:120]}")
    report.add("no_hardcoded_absolute_paths", not bad, bad)


def main() -> int:
    logger.info("Loading integrated graph: %s", INTEGRATED_GRAPH)
    if not INTEGRATED_GRAPH.is_file():
        logger.error("Integrated graph not found: %s", INTEGRATED_GRAPH)
        return 1
    graph = load_json(INTEGRATED_GRAPH)
    nodes, edges = graph.get("nodes", []), graph.get("edges", [])
    logger.info("Loaded %d nodes, %d edges", len(nodes), len(edges))

    report = Report()
    check_edges_endpoints(nodes, edges, report)
    check_edge_sources(nodes, edges, report)
    check_hidden_states(nodes, edges, report)
    check_guardrails(nodes, edges, report)
    check_measured_parameters(nodes, report)
    check_duplicates(nodes, edges, report)
    check_orphan_sources(nodes, edges, report)
    check_count_claims(nodes, edges, report)
    check_no_hardcoded_paths(report)

    passed = sum(1 for _, ok, _ in report.results if ok)
    total = len(report.results)
    print("\n" + "=" * 60)
    print("SEMANTIC INTEGRITY REPORT")
    print("=" * 60)
    for name, ok, _ in report.results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print("=" * 60)
    if report.ok:
        logger.info("=== Semantic integrity PASS (%d/%d checks) ===", passed, total)
        return 0
    logger.error("=== Semantic integrity FAIL (%d/%d checks) ===", passed, total)
    return 1


if __name__ == "__main__":
    sys.exit(main())
