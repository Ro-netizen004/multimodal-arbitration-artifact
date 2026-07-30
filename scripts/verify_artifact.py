#!/usr/bin/env python3
"""Verify artifact checksums, size limits, and basic anonymity constraints."""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {
    "personal identity": re.compile(
        "Rode" + r"la|Ro-netizen|rg" + r"21|Tech moon", re.IGNORECASE
    ),
    "institutional cluster": re.compile(
        "gai" + r"vi|forest[.]usf|University of South Florida", re.IGNORECASE
    ),
    "personal absolute path": re.compile(
        r"/home/r/|/data/rg" + r"21|[A-Za-z]:\\Users\\", re.IGNORECASE
    ),
    "token-shaped secret": re.compile(
        r"hf_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]+|ghp_[A-Za-z0-9]+"
    ),
}
TEXT_SUFFIXES = {
    ".csv", ".json", ".jsonl", ".md", ".py", ".sh", ".txt", ".yaml", ".yml"
}


def main():
    manifest_path = ROOT / "MANIFEST.json"
    if not manifest_path.exists():
        raise SystemExit("MANIFEST.json is missing.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {row["path"]: row for row in manifest["files"]}
    actual = {
        path.relative_to(ROOT).as_posix(): path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.name != "MANIFEST.json"
        and ".git" not in path.parts
        and ".venv" not in path.parts
        and "reproduced" not in path.parts
        and "__pycache__" not in path.parts
    }
    errors = []
    for relative in sorted(set(expected) - set(actual)):
        errors.append(f"missing file: {relative}")
    for relative in sorted(set(actual) - set(expected)):
        errors.append(f"unmanifested file: {relative}")
    for relative in sorted(set(expected) & set(actual)):
        path = actual[relative]
        payload = path.read_bytes()
        if len(payload) != expected[relative]["bytes"]:
            errors.append(f"size mismatch: {relative}")
        if hashlib.sha256(payload).hexdigest() != expected[relative]["sha256"]:
            errors.append(f"checksum mismatch: {relative}")
        if len(payload) >= 100 * 1024 * 1024:
            errors.append(f"file is at least 100 MiB: {relative}")
        if path.suffix.lower() in TEXT_SUFFIXES and path.name != "verify_artifact.py":
            value = payload.decode("utf-8", errors="replace")
            for label, pattern in FORBIDDEN.items():
                if pattern.search(value):
                    errors.append(f"{label}: {relative}")
    if errors:
        print("Artifact verification FAILED:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    size = sum(path.stat().st_size for path in actual.values())
    print(
        f"Artifact verification passed: {len(actual)} manifested files, "
        f"{size / (1024 ** 2):.2f} MiB."
    )


if __name__ == "__main__":
    main()
