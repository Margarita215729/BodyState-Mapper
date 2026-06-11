#!/usr/bin/env python3
"""Convert evidence registry and static edges between CSV and JSON formats."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any

from _project_paths import (
    EDGE_FIELDS,
    EDGES_CSV,
    EDGES_JSON,
    REGISTRY_CSV,
    REGISTRY_FIELDS,
    REGISTRY_JSON,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_source_ids(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    text = str(raw).strip()
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def format_source_ids(ids: list[str]) -> str:
    return ";".join(ids)


def coerce_registry_row(row: dict[str, str]) -> dict[str, Any]:
    item: dict[str, Any] = {field: row.get(field, "") or "" for field in REGISTRY_FIELDS}
    if item["year"]:
        try:
            item["year"] = int(str(item["year"]))
        except ValueError:
            pass
    if item["evidence_strength_score"]:
        try:
            item["evidence_strength_score"] = int(str(item["evidence_strength_score"]))
        except ValueError:
            pass
    return item


def coerce_edge_row(row: dict[str, str]) -> dict[str, Any]:
    item: dict[str, Any] = {field: row.get(field, "") or "" for field in EDGE_FIELDS}
    item["source_ids"] = parse_source_ids(item.get("source_ids", ""))
    if item["evidence_strength_score"]:
        try:
            item["evidence_strength_score"] = int(str(item["evidence_strength_score"]))
        except ValueError:
            pass
    return item


def read_csv(path: Path, fields: list[str], coerce) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, Any]] = []
        for row in reader:
            if not any(v.strip() for v in row.values() if v):
                continue
            normalized = {field: row.get(field, "") or "" for field in fields}
            rows.append(coerce(normalized))
        return rows


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            out = {field: row.get(field, "") for field in fields}
            if "source_ids" in out:
                out["source_ids"] = format_source_ids(parse_source_ids(out["source_ids"]))
            writer.writerow(out)
    logger.info("Wrote CSV (%d rows): %s", len(rows), path)


def write_json(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    logger.info("Wrote JSON (%d rows): %s", len(rows), path)


def export_registry_csv_to_json(csv_path: Path, json_path: Path) -> None:
    rows = read_csv(csv_path, REGISTRY_FIELDS, coerce_registry_row)
    write_json(json_path, rows)


def export_registry_json_to_csv(json_path: Path, csv_path: Path) -> None:
    rows = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("Registry JSON must be an array.")
    write_csv(csv_path, REGISTRY_FIELDS, rows)


def export_edges_csv_to_json(csv_path: Path, json_path: Path) -> None:
    rows = read_csv(csv_path, EDGE_FIELDS, coerce_edge_row)
    write_json(json_path, rows)


def export_edges_json_to_csv(json_path: Path, csv_path: Path) -> None:
    rows = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("Edges JSON must be an array.")
    write_csv(csv_path, EDGE_FIELDS, rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert THSI registry/edges between CSV and JSON."
    )
    parser.add_argument(
        "target",
        choices=["registry", "edges", "all"],
        help="Which dataset to convert.",
    )
    parser.add_argument(
        "direction",
        choices=["csv-to-json", "json-to-csv"],
        help="Conversion direction.",
    )
    parser.add_argument("--csv", type=Path, default=None, help="Override CSV path.")
    parser.add_argument("--json", type=Path, default=None, help="Override JSON path.")
    args = parser.parse_args()

    targets = ["registry", "edges"] if args.target == "all" else [args.target]

    for target in targets:
        if target == "registry":
            csv_path = args.csv or REGISTRY_CSV
            json_path = args.json or REGISTRY_JSON
            if args.direction == "csv-to-json":
                export_registry_csv_to_json(csv_path, json_path)
            else:
                export_registry_json_to_csv(json_path, csv_path)
        else:
            csv_path = args.csv or EDGES_CSV
            json_path = args.json or EDGES_JSON
            if args.direction == "csv-to-json":
                export_edges_csv_to_json(csv_path, json_path)
            else:
                export_edges_json_to_csv(json_path, csv_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
