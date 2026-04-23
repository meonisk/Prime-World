#!/usr/bin/env python3
"""Download and extract large asset archives referenced by manifest.json.

The repo stores only code + metadata; heavy binaries live as zip archives on
Google Drive. This script fetches the archives listed in
tools/assets/manifest.json, verifies sha256, and extracts them into the repo
root so that paths line up with what the engine and editor expect.

Requires only Python 3.8+ — no third-party dependencies.
  Windows 10+:  py tools\\assets\\fetch_assets.py --all
  Linux/macOS:  python3 tools/assets/fetch_assets.py --all
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = Path(__file__).resolve().parent / "manifest.json"
MARKER_PATH = REPO_ROOT / ".assets-fetched"

# Direct-download endpoint for public Drive files. The `confirm=t` bypasses
# the >100 MB virus-scan interstitial without a token dance.
DRIVE_DOWNLOAD_URL = "https://drive.usercontent.google.com/download?id={id}&export=download&confirm=t"
USER_AGENT = "Mozilla/5.0 (PrimeWorld fetch_assets.py)"
CHUNK = 1 << 20  # 1 MiB


def load_manifest() -> dict:
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def load_marker() -> dict:
    if not MARKER_PATH.exists():
        return {}
    try:
        return json.loads(MARKER_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_marker(marker: dict) -> None:
    MARKER_PATH.write_text(json.dumps(marker, indent=2, sort_keys=True), encoding="utf-8")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def human_mb(n: int) -> str:
    return f"{n / (1024 * 1024):.1f} MB"


def stream_download(url: str, dest: Path, expected_size: int = 0) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as response:
        total = expected_size or int(response.headers.get("Content-Length") or 0)
        downloaded = 0
        start = time.monotonic()
        last_print = 0.0
        is_tty = sys.stderr.isatty()
        with dest.open("wb") as fh:
            while True:
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                fh.write(chunk)
                downloaded += len(chunk)
                now = time.monotonic()
                if now - last_print >= 0.3:
                    elapsed = max(now - start, 0.001)
                    speed = downloaded / elapsed / (1024 * 1024)
                    if total:
                        pct = downloaded * 100 // total
                        msg = f"  {pct:3d}%  {human_mb(downloaded)} / {human_mb(total)}  {speed:5.1f} MB/s"
                    else:
                        msg = f"  {human_mb(downloaded)}  {speed:5.1f} MB/s"
                    if is_tty:
                        sys.stderr.write("\r" + msg + "    ")
                    else:
                        sys.stderr.write(msg + "\n")
                    sys.stderr.flush()
                    last_print = now
        if is_tty:
            sys.stderr.write("\n")
            sys.stderr.flush()


def download_drive_file(gdrive_id: str, dest: Path, expected_size: int, attempts: int = 4) -> None:
    url = DRIVE_DOWNLOAD_URL.format(id=gdrive_id)
    last_exc: BaseException | None = None
    backoff = 2
    for i in range(1, attempts + 1):
        try:
            stream_download(url, dest, expected_size)
            if not dest.exists() or dest.stat().st_size == 0:
                raise RuntimeError("downloaded file is empty")
            if expected_size and dest.stat().st_size != expected_size:
                raise RuntimeError(
                    f"size mismatch: expected {expected_size} bytes, got {dest.stat().st_size}"
                )
            return
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, RuntimeError) as exc:
            last_exc = exc
            print(f"  attempt {i}/{attempts} failed: {exc}", file=sys.stderr)
            if dest.exists():
                try:
                    dest.unlink()
                except OSError:
                    pass
            if i < attempts:
                time.sleep(backoff)
                backoff *= 2
    raise RuntimeError(f"failed to download {gdrive_id}: {last_exc}")


def extract_zip(zip_path: Path, extract_to: Path) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extract_to)


def select_archives(manifest: dict, tags: list[str], include_all: bool) -> list[dict]:
    archives = manifest["archives"]
    if include_all:
        return archives
    if not tags:
        return [a for a in archives if a.get("required")]
    wanted = set(tags)
    return [a for a in archives if a.get("tag") in wanted]


def fetch_archive(entry: dict, marker: dict, force: bool, verify_only: bool) -> None:
    name = entry["name"]
    gdrive_id = entry.get("gdrive_id")
    expected_sha = entry.get("sha256")
    expected_size = int(entry.get("size_bytes") or 0)
    extract_to = REPO_ROOT / entry.get("extract_to", ".")

    if not gdrive_id or gdrive_id == "TODO":
        print(f"[{name}] skipped: gdrive_id is not set in manifest")
        return
    if not expected_sha or expected_sha == "TODO":
        print(f"[{name}] skipped: sha256 is not set in manifest")
        return

    if not force and marker.get(name, {}).get("sha256") == expected_sha:
        print(f"[{name}] already fetched (sha matches marker)")
        return

    if verify_only:
        print(f"[{name}] verify-only: nothing on disk to verify without refetch")
        return

    size_hint = f" ({human_mb(expected_size)})" if expected_size else ""
    print(f"[{name}] downloading from Google Drive id={gdrive_id}{size_hint} ...")
    with tempfile.TemporaryDirectory(prefix=f"pw-{name}-") as td:
        zip_path = Path(td) / f"{name}.zip"
        download_drive_file(gdrive_id, zip_path, expected_size)

        actual_sha = sha256_of(zip_path)
        if actual_sha != expected_sha:
            raise RuntimeError(
                f"[{name}] sha256 mismatch: expected {expected_sha}, got {actual_sha}"
            )
        print(f"[{name}] sha256 OK, extracting to {extract_to} ...")
        extract_to.mkdir(parents=True, exist_ok=True)
        extract_zip(zip_path, extract_to)

    marker[name] = {"sha256": expected_sha, "fetched_at": int(time.time())}
    save_marker(marker)
    print(f"[{name}] done.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch and extract Prime-World asset archives from Google Drive."
    )
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Select archives by tag (repeatable): assets, source, vendor, locale, misc.",
    )
    parser.add_argument("--all", action="store_true", help="Fetch every archive in the manifest.")
    parser.add_argument(
        "--force", action="store_true", help="Re-download even if the marker matches."
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Only check the marker against the manifest; do not download.",
    )
    parser.add_argument("--list", action="store_true", help="Print manifest entries and exit.")
    args = parser.parse_args()

    manifest = load_manifest()

    if args.list:
        for a in manifest["archives"]:
            print(
                f"  {a['name']:<24} tag={a.get('tag'):<8} required={a.get('required')} "
                f"size={a.get('size_bytes')} gdrive_id={a.get('gdrive_id')}"
            )
        return 0

    marker = load_marker()

    selected = select_archives(manifest, args.tag, args.all)
    if not selected:
        print("No archives selected. Use --all, or --tag=<assets|source|vendor|locale|misc>.")
        return 1

    for entry in selected:
        try:
            fetch_archive(entry, marker, args.force, args.verify)
        except Exception as exc:
            print(f"[{entry['name']}] ERROR: {exc}", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
