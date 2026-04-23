#!/usr/bin/env python3
"""Build zip archives described in manifest.json from the current working tree.

Run this once, before history is rewritten, while all the large files still
exist on disk. It produces one zip per manifest entry, prints sha256 + size,
and leaves a ready-to-upload file per archive under `dist/assets-archives/`.

After uploading the zips to Google Drive (public folder), paste the file ids
(and the sha256 + size this script prints) back into manifest.json.

Requires: Python 3.8+.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = Path(__file__).resolve().parent / "manifest.json"
DEFAULT_OUT = REPO_ROOT / "dist" / "assets-archives"


def load_manifest() -> dict:
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def iter_source_files(source: Path, include_globs: list[str] | None):
    if source.is_file():
        yield source
        return
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        if include_globs:
            rel = path.relative_to(REPO_ROOT).as_posix()
            if not any(fnmatch.fnmatch(rel, g) for g in include_globs):
                continue
        yield path


def build_archive(entry: dict, out_dir: Path) -> dict:
    name = entry["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"{name}.zip"
    include_globs = entry.get("include_globs")

    print(f"[{name}] building {zip_path} ...")
    total_files = 0
    total_bytes = 0
    # ZIP_STORED gives us a useful archive even when the payload is already
    # compressed (dds/fsb/exe/lib); ZIP_DEFLATED barely helps and is much
    # slower on 6 GB of binary data.
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as zf:
        for source_rel in entry["sources"]:
            source = REPO_ROOT / source_rel
            if not source.exists():
                print(f"  warning: source missing: {source_rel}", file=sys.stderr)
                continue
            for path in iter_source_files(source, include_globs):
                arcname = path.relative_to(REPO_ROOT).as_posix()
                zf.write(path, arcname)
                total_files += 1
                total_bytes += path.stat().st_size

    size = zip_path.stat().st_size
    sha = sha256_of(zip_path)
    print(
        f"[{name}] files={total_files} raw={total_bytes} zip={size} sha256={sha}"
    )
    return {
        "name": name,
        "zip_path": str(zip_path),
        "sha256": sha,
        "size_bytes": size,
        "files": total_files,
    }


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the asset zip archives described in manifest.json."
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output directory.")
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Only build the listed archive name(s); default: all.",
    )
    args = parser.parse_args()

    manifest = load_manifest()
    wanted = set(args.only)
    entries = [a for a in manifest["archives"] if not wanted or a["name"] in wanted]
    if not entries:
        print("No matching archive entries in manifest.", file=sys.stderr)
        return 1

    results = [build_archive(e, args.out) for e in entries]

    print("\nSummary (paste into manifest.json after uploading to Google Drive):")
    print(f"{'name':<24} {'size_bytes':>14}  sha256")
    for r in results:
        print(f"{r['name']:<24} {r['size_bytes']:>14}  {r['sha256']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
