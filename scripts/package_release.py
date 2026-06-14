#!/usr/bin/env python3
"""
Build a clean release archive of the BodyState Mapper / THSI project.

Produces dist/BodyState_Mapper_clean_release_v1_0.zip.

Excludes (never shipped):
  - .git/ and any VCS internals
  - .DS_Store, __MACOSX/
  - __pycache__/, *.pyc, *.pyo
  - .pytest_cache/, .mypy_cache/
  - local environments (venv/, .venv/, env/)
  - editor folders (.idea/, .vscode/)
  - the dist/ output directory itself
  - nested zip archives unless explicitly whitelisted
  - temporary files (*.tmp, *.tmp.zip)

Prints the files included, the files excluded, the final zip path, and its size.
Exits non-zero on failure.
"""

from __future__ import annotations

import logging
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _project_paths import PROJECT_ROOT  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("package_release")

DIST_DIR = PROJECT_ROOT / "dist"
RELEASE_NAME = "BodyState_Mapper_clean_release_v1_0.zip"
RELEASE_PATH = DIST_DIR / RELEASE_NAME

EXCLUDED_DIR_NAMES = {
    ".git",
    "__MACOSX",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "venv",
    ".venv",
    "env",
    ".idea",
    ".vscode",
    "dist",
}

EXCLUDED_FILE_NAMES = {".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp"}

# Zip archives are excluded unless whitelisted here (relative POSIX paths).
WHITELISTED_ZIPS: set[str] = set()


def is_excluded(rel: Path) -> tuple[bool, str]:
    parts = rel.parts
    for part in parts[:-1] + (parts[-1],):
        if part in EXCLUDED_DIR_NAMES:
            return True, f"excluded dir '{part}'"
    name = rel.name
    if name in EXCLUDED_FILE_NAMES:
        return True, "excluded file name"
    suffix = rel.suffix.lower()
    if suffix in EXCLUDED_SUFFIXES:
        return True, f"excluded suffix '{suffix}'"
    if name.endswith(".tmp.zip"):
        return True, "temporary zip"
    if suffix == ".zip" and rel.as_posix() not in WHITELISTED_ZIPS:
        return True, "non-whitelisted zip archive"
    return False, ""


def collect_files() -> tuple[list[Path], list[tuple[Path, str]]]:
    included: list[Path] = []
    excluded: list[tuple[Path, str]] = []
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(PROJECT_ROOT)
        skip, reason = is_excluded(rel)
        if skip:
            excluded.append((rel, reason))
        else:
            included.append(rel)
    return included, excluded


def main() -> int:
    logger.info("Packaging release from %s", PROJECT_ROOT)
    included, excluded = collect_files()

    if not included:
        logger.error("No files to include; aborting.")
        return 1

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    if RELEASE_PATH.exists():
        RELEASE_PATH.unlink()

    with zipfile.ZipFile(RELEASE_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in included:
            zf.write(PROJECT_ROOT / rel, arcname=str(rel))

    print("\n" + "=" * 70)
    print("INCLUDED FILES (%d):" % len(included))
    print("=" * 70)
    for rel in included:
        print(f"  + {rel.as_posix()}")

    print("\n" + "=" * 70)
    print("EXCLUDED FILES (%d):" % len(excluded))
    print("=" * 70)
    for rel, reason in excluded:
        print(f"  - {rel.as_posix()}  [{reason}]")

    size = RELEASE_PATH.stat().st_size
    size_mb = size / (1024 * 1024)
    print("\n" + "=" * 70)
    print(f"Release archive : {RELEASE_PATH}")
    print(f"Files included  : {len(included)}")
    print(f"Files excluded  : {len(excluded)}")
    print(f"Archive size    : {size:,} bytes ({size_mb:.2f} MB)")
    print("=" * 70)
    logger.info("Wrote %s (%.2f MB)", RELEASE_PATH, size_mb)
    return 0


if __name__ == "__main__":
    sys.exit(main())
