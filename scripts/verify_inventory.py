#!/usr/bin/env python3
"""Offline source-integrity and reviewed capability-contract validation.

The resource inventory is authoritative for shipped bytes and provenance.
The optional capability catalog is intentionally sparse: it neither claims
all installed Lua/BIN files are executable nor acts as a filename whitelist.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

SAFE_NAME = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]*$")
SAFE_VALUE = re.compile(r"^[A-Za-z0-9_,.+-]+$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")


def valid_target(target: object) -> bool:
    if not isinstance(target, str):
        return False
    path = pathlib.PurePosixPath(target)
    if (path.is_absolute() or any(part in {".", ".."} for part in target.split("/"))
            or not all(SAFE_NAME.fullmatch(part) for part in path.parts)):
        return False
    return (
        (len(path.parts) == 2 and path.parts[0] == "lua"
         and path.suffix == ".lua")
        or (len(path.parts) == 3 and path.parts[:2] == ("files", "fake")
            and path.suffix == ".bin")
    )


def checked_file(root: pathlib.Path, rel: str) -> bytes:
    file = root / rel
    if file.is_symlink() or not file.is_file():
        raise ValueError(f"missing/non-regular/symlink resource: {rel}")
    return file.read_bytes()


def check_capabilities(root: pathlib.Path, registered: dict[str, dict],
                       errors: list[str]) -> int:
    path = root / "inventory" / "capabilities.json"
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"capability catalog unreadable: {exc}")
        return 0
    if (not isinstance(catalog, dict) or catalog.get("schema") != 1
            or not isinstance(catalog.get("resources"), list)):
        errors.append("capability catalog schema must be 1 with resources array")
        return 0
    seen: set[str] = set()
    for entry in catalog["resources"]:
        if not isinstance(entry, dict):
            errors.append("capability entry must be an object")
            continue
        target = entry.get("target")
        if not valid_target(target) or target not in registered:
            errors.append(f"capability references unlisted/invalid target: {target}")
            continue
        if target in seen:
            errors.append(f"duplicate capability declaration: {target}")
            continue
        seen.add(target)
        try:
            data = checked_file(root, target)
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
            continue
        if not data:
            errors.append(f"empty executable resource: {target}")
            continue
        expected_kind = "lua" if target.startswith("lua/") else "blob"
        if entry.get("kind") != expected_kind:
            errors.append(f"capability kind differs from resource path: {target}")
            continue
        if entry.get("protocol") not in {"tls13", "tls12", "http", "quic", "udp"}:
            errors.append(f"unsupported protocol descriptor: {target}")
        if entry.get("transport") not in {"tcp", "udp"}:
            errors.append(f"unsupported transport descriptor: {target}")
        if not isinstance(entry.get("family"), str) or not SAFE_NAME.fullmatch(entry["family"]):
            # Established families may include '+', which is permitted by SAFE_NAME.
            errors.append(f"invalid family descriptor: {target}")
        if expected_kind == "blob":
            if entry.get("native_action") not in {"fake", "seqovl"}:
                errors.append(f"unsupported native BLOB action: {target}")
            if entry.get("argument") not in {"blob", "seqovl_pattern"}:
                errors.append(f"unsupported BLOB argument: {target}")
            fmt = entry.get("format")
            if fmt == "tls-clienthello":
                # A TLS record with a ClientHello handshake. Does not assert
                # that this is a syntactically complete or successful bypass.
                if (len(data) < 6 or data[0] != 0x16 or data[1] != 0x03
                        or data[2] > 0x04 or data[5] != 0x01):
                    errors.append(f"declared TLS ClientHello signature missing: {target}")
                if entry.get("transport") != "tcp" or entry.get("protocol") not in {"tls12", "tls13"}:
                    errors.append(f"TLS record classified with incompatible transport: {target}")
            else:
                errors.append(f"unverified BLOB format: {target}")
        else:
            if entry.get("role") != "desync":
                errors.append(f"unsupported Lua role: {target}")
            export = entry.get("export")
            if not isinstance(export, str) or not SAFE_NAME.fullmatch(export):
                errors.append(f"invalid Lua export: {target}")
            elif not re.search(r"(?m)^\s*function\s+" + re.escape(export) + r"\s*\(", data.decode("utf-8", errors="replace")):
                errors.append(f"declared top-level Lua export absent: {target}:{export}")
            deps = entry.get("dependencies")
            if (not isinstance(deps, list) or not deps or len(set(str(x) for x in deps)) != len(deps)
                    or any(not isinstance(x, str) or not x.endswith(".lua")
                           or not SAFE_NAME.fullmatch(x) for x in deps)):
                errors.append(f"invalid Lua dependencies: {target}")
            args = entry.get("arguments")
            if (not isinstance(args, list) or not args
                    or any(not isinstance(x, dict)
                           or not isinstance(x.get("name"), str)
                           or not SAFE_NAME.fullmatch(x["name"])
                           or not isinstance(x.get("value"), str)
                           or not SAFE_VALUE.fullmatch(x["value"]) for x in args)):
                errors.append(f"invalid Lua argument descriptors: {target}")
    return len(seen)


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    errors: list[str] = []
    manifest = json.loads((root / "inventory" / "sources.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != 1 or not isinstance(manifest.get("resources"), list):
        print("FAIL: invalid source inventory schema", file=sys.stderr)
        return 1
    registered: dict[str, dict] = {}
    seen_sha: dict[str, str] = {}
    for item in manifest["resources"]:
        if not isinstance(item, dict):
            errors.append("source entry is not an object")
            continue
        rel = item.get("target")
        if not valid_target(rel):
            errors.append(f"invalid source path: {rel}")
            continue
        if rel in registered:
            errors.append(f"repeated manifest path: {rel}")
            continue
        registered[rel] = item
        try:
            data = checked_file(root, rel)
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
            continue
        sha = item.get("sha")
        git_sha = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        if not isinstance(sha, str) or not GIT_SHA.fullmatch(sha) or git_sha != sha:
            errors.append(f"hash mismatch: {rel}")
        if item.get("size") != len(data):
            errors.append(f"size mismatch: {rel}")
        if not data:
            errors.append(f"empty source resource: {rel}")
        if git_sha in seen_sha:
            errors.append(f"duplicate data: {seen_sha[git_sha]} == {rel}")
        seen_sha[git_sha] = rel

    actual = {
        p.relative_to(root).as_posix()
        for pattern in ("lua/*.lua", "files/fake/*.bin")
        for p in root.glob(pattern)
    }
    for rel in sorted(actual - set(registered)):
        errors.append(f"unlisted resource: {rel}")
    if len(manifest["resources"]) != manifest.get("total") or len(actual) != len(registered):
        errors.append("resource total/count mismatch")
    counts = {"lua": sum(x.startswith("lua/") for x in registered),
              "bin": sum(x.startswith("files/fake/") for x in registered)}
    if manifest.get("counts") != counts:
        errors.append("manifest type counts mismatch")
    described = check_capabilities(root, registered, errors)
    for error in errors:
        print("FAIL:", error, file=sys.stderr)
    if errors:
        return 1
    print(f"PASS: {len(registered)} source files, verified bytes and provenance; "
          f"{described} explicit capabilities validated; undescribed resources are unsupported")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
