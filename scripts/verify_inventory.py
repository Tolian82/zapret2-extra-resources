#!/usr/bin/env python3
"""Offline integrity and deduplication check for the published resource catalog."""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "inventory" / "sources.json").read_text(encoding="utf-8"))
    items = manifest["resources"]
    expected = {}
    seen_sha = {}
    errors = []

    for item in items:
        rel = item["target"]
        path = pathlib.PurePosixPath(rel)
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"invalid path: {rel}")
            continue
        if not (
            (len(path.parts) == 2 and path.parts[0] == "lua" and path.suffix == ".lua") or
            (len(path.parts) == 3 and path.parts[:2] == ("files", "fake") and path.suffix == ".bin")
        ):
            errors.append(f"unexpected target path: {rel}")
            continue
        if rel in expected:
            errors.append(f"repeated manifest path: {rel}")
        expected[rel] = item["sha"]
        disk = root / rel
        if not disk.is_file():
            errors.append(f"missing file: {rel}")
            continue
        data = disk.read_bytes()
        git_sha = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + bytes([0]) + data).hexdigest()
        if git_sha != item["sha"]:
            errors.append(f"hash mismatch: {rel}: expected {item['sha']}, actual {git_sha}")
        if git_sha in seen_sha and seen_sha[git_sha] != rel:
            errors.append(f"duplicate data: {seen_sha[git_sha]} == {rel}")
        seen_sha[git_sha] = rel

    actual = {
        p.relative_to(root).as_posix()
        for pattern in ("lua/*.lua", "files/fake/*.bin")
        for p in root.glob(pattern)
    }
    for rel in sorted(actual - set(expected)):
        errors.append(f"unlisted resource: {rel}")
    if len(items) != manifest["total"]:
        errors.append("manifest total differs from resources length")
    if len(actual) != len(items):
        errors.append(f"resource count mismatch: listed={len(items)} on disk={len(actual)}")
    for err in errors:
        print("FAIL:", err, file=sys.stderr)
    if errors:
        return 1
    print(f"PASS: {len(items)} resources present, pinned Git blob hashes match, no duplicate content")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
