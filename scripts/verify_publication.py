"""Audit the selected publication history and the exact checked-out input bytes."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image

from myoshift.provenance import verify


def forbidden_patterns() -> tuple[str, ...]:
    names = (
        "chat" + "gpt",
        "co" + "dex",
        "cla" + "ude",
        "cur" + "sor",
        "o" + "penai",
        "an" + "thropic",
        "gem" + "ini",
        "gro" + "k",
        "cop" + "ilot",
        "per" + "plexity",
        "ki" + "mi",
        "deep" + "seek",
        "gpt" + r"[- ]?\d[\w.-]*",
        "o" + r"[134]\b",
        "lu" + "na",
        "ter" + "ra",
        "fa" + "ble",
    )
    return (
        "/" + "Users/",
        "/" + "private/",
        "/" + "var/folders/",
        chr(0x2014),
        r"\b(?:" + "|".join(names) + r")\b",
        "flagship_gates__" + "pplx",
    )


def has_forbidden(text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in forbidden_patterns())


def git(root: Path, *arguments: str) -> bytes:
    return subprocess.check_output(  # noqa: S603
        ["/usr/bin/git", *arguments], cwd=root, stderr=subprocess.PIPE
    )


def object_text(body: bytes) -> tuple[str, bool]:
    """Read UTF-8 content or verified PNG metadata, never compressed pixel noise."""
    try:
        return body.decode("utf-8"), False
    except UnicodeError:
        if not body.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("unsupported non-text publication object") from None
        with Image.open(io.BytesIO(body)) as picture:
            metadata = dict(picture.info)
            picture.verify()
        return json.dumps(metadata, default=str), True


def audit_history(root: Path, ref: str = "HEAD") -> dict[str, Any]:
    if git(root, "rev-parse", "--is-shallow-repository").strip() == b"true":
        raise ValueError("publication audit requires full history; shallow checkout rejected")
    commit = git(root, "rev-parse", "--verify", ref + "^{commit}").decode().strip()
    tree = git(root, "rev-parse", commit + "^{tree}").decode().strip()
    objects = git(root, "rev-list", "--objects", ref).decode().splitlines()
    violations: list[str] = []
    counts: dict[str, int] = {}
    png_metadata_blobs = 0
    seen = set()
    # Annotated tags pointing into this history are inspected even when the selected
    # ref itself is a branch or detached commit. Unrelated development refs are excluded.
    reachable_commits = set(git(root, "rev-list", commit).decode().splitlines())
    for tag in git(root, "for-each-ref", "--format=%(refname)", "refs/tags").decode().splitlines():
        target = git(root, "rev-parse", tag + "^{}").decode().strip()
        if target in reachable_commits:
            objects.append(git(root, "rev-parse", tag).decode().strip() + " " + tag)
    for entry in objects:
        oid, _, name = entry.partition(" ")
        if name and has_forbidden(name):
            violations.append("path:" + name)
        if oid in seen:
            continue
        seen.add(oid)
        kind = git(root, "cat-file", "-t", oid).decode().strip()
        counts[kind] = counts.get(kind, 0) + 1
        body = git(root, "cat-file", "-p", oid)
        text, binary = object_text(body)
        png_metadata_blobs += int(binary)
        if has_forbidden(text):
            violations.append(kind + ":" + oid)
        if kind == "tree":
            # Inspect every path in every historical tree, including renamed blobs.
            for path in git(root, "ls-tree", "-r", "--name-only", "-z", oid).split(b"\0"):
                if has_forbidden(path.decode("utf-8", errors="replace")):
                    violations.append("tree-path:" + oid)
    return {
        "commit": commit,
        "tree": tree,
        "objects": counts,
        "png_metadata_blobs": png_metadata_blobs,
        "violations": sorted(set(violations)),
    }


def receipt(root: Path, ref: str, data_root: Path) -> dict[str, Any]:
    audit = audit_history(root, ref)
    if audit["violations"]:
        raise ValueError("publication history hygiene failed: " + str(audit["violations"]))
    if git(root, "status", "--porcelain", "--untracked-files=no").strip():
        raise ValueError("publication receipt requires a clean tracked checkout")
    data = json.loads((root / "results/results.json").read_text())
    counts = verify(root, data, data_root)
    tracked = git(root, "ls-files", "-z").decode().split("\0")
    file_hashes = {
        path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in tracked if path
    }
    return {
        "audit": audit,
        "verified": counts,
        "tracked_sha256": file_hashes,
        "provenance": data["provenance"],
        "byte_policy": "ordinary text LF; frozen protocol and checksum bytes verbatim",
        "roles": {"source_sha256": "publication inputs", "data_sha256": "upstream waveform/header"},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--data-root", type=Path, default=Path("data/raw/grabmyo-flow/static_extension_WFDB")
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="External companion receipt path"
    )
    args = parser.parse_args()
    result = receipt(args.root.resolve(), args.ref, args.data_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"hygiene_hits": 0, **result["verified"], **result["audit"]["objects"]}))


if __name__ == "__main__":
    main()
