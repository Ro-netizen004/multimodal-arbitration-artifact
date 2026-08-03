#!/usr/bin/env python3
"""Verify artifact checksums, size limits, and basic anonymity constraints."""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {
    "email address": re.compile(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE
    ),
    "personal absolute path": re.compile(
        r"/home/r/|/data/rg" + r"21|[A-Za-z]:\\Users\\", re.IGNORECASE
    ),
    "token-shaped secret": re.compile(
        r"hf_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]+|ghp_[A-Za-z0-9]+"
    ),
}
# SHA-256 digests reject project-specific identifying tokens without publishing
# those tokens in the anonymous artifact. The token scan is limited to small
# metadata/code files; generic path, email, and secret checks still cover all
# textual outputs.
FORBIDDEN_TOKEN_HASHES = {
    "0cbf857023e7b8d88e60566429f6f4e9031549ec695ea3a6406c7a0f408c6229",
    "b3ee2a758e6352060dfcbe347d4f5bc48bb95afa633b3d11339e3eb31226cf9a",
    "7196dc911f4f68b2e997dce291e2b42e0d3d69f746dc80d4ebeccd504af1b28e",
    "d389f2fe204a555c8b212fc2b5774be2d2c5fa731052197f61d56219f6200ccb",
    "09e42d840905c824766bfa303bf5ae609e52c2aa27a7cc3e491614026d827331",
    "23e7e646939e173ea6b6b160c757f12c8157e335f0d5f568993333be4c44c0df",
    "49b6e65154771d059aaad07c9bdac87368767058bb66c64b8f12e228698ab0b1",
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
            if len(payload) < 256 * 1024:
                tokens = re.findall(r"[A-Za-z0-9._-]+", value.casefold())
                if any(
                    hashlib.sha256(token.encode("utf-8")).hexdigest()
                    in FORBIDDEN_TOKEN_HASHES
                    for token in tokens
                ):
                    errors.append(f"project-specific identity token: {relative}")
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
