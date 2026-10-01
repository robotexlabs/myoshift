"""Release acceptance, download failure isolation and portable benchmark checks."""

from __future__ import annotations

import fnmatch
import hashlib
import importlib.util
import io
import json
import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from scripts.verify_publication import audit_history, has_forbidden

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pilot_download", ROOT / "scripts/download_pilot.py")
assert SPEC is not None and SPEC.loader is not None
DOWNLOAD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DOWNLOAD)


class Response(io.BytesIO):
    headers: dict[str, str] = {}


@pytest.mark.parametrize("failure", ["corrupt", "oversized", "interrupted"])
def test_transfer_failure_preserves_target(tmp_path: Path, failure: str) -> None:
    target = tmp_path / "record.dat"
    target.write_bytes(b"original")
    response = Response(b"invalid payload")
    if failure == "interrupted":
        response.read = lambda _: (_ for _ in ()).throw(ConnectionError("interrupted"))
    limit = 3 if failure == "oversized" else 100
    with (
        patch.object(DOWNLOAD.urllib.request, "urlopen", return_value=response),
        pytest.raises((ValueError, ConnectionError)),
    ):
        DOWNLOAD.fetch(DOWNLOAD.UPSTREAM + "record.dat", target, "0" * 64, limit)
    assert target.read_bytes() == b"original"
    assert list(tmp_path.glob("*.part")) == []


def test_verified_transfer_promotes_atomically(tmp_path: Path) -> None:
    target = tmp_path / "record.dat"
    payload = b"verified bytes"
    with patch.object(DOWNLOAD.urllib.request, "urlopen", return_value=Response(payload)):
        assert DOWNLOAD.fetch(
            DOWNLOAD.UPSTREAM + "record.dat", target, hashlib.sha256(payload).hexdigest(), 100
        ) == len(payload)
    assert target.read_bytes() == payload


def test_aggregate_transfer_budget(tmp_path: Path) -> None:
    limits = []

    def fetch(url: str, target: Path, expected: str | None, limit: int) -> int:
        limits.append(limit)
        if expected is None:
            entries = []
            for participant in (44, 45, 46, 47):
                for session in (1, 2, 3):
                    for gesture in (1, 2, 3, 17):
                        for trial in (1, 2):
                            base = (
                                f"static_extension_WFDB/session{session}/"
                                f"session{session}_participant{participant}/"
                                f"session{session}_participant{participant}_gesture{gesture}"
                                f"_trial{trial}"
                            )
                            entries.extend(f"{'0' * 64}  {base}.{ext}" for ext in ("hea", "dat"))
            target.write_text("\n".join(entries))
            return 10
        if limit < 10:
            raise ValueError("download exceeds byte cap")
        return 10

    with (
        patch.object(DOWNLOAD, "fetch", fetch),
        patch.object(DOWNLOAD, "MAX_BYTES", 25),
        pytest.raises(ValueError, match="byte cap"),
    ):
        DOWNLOAD.download(tmp_path)
    assert limits[1:] == [15, 5]


@pytest.mark.network
def test_clean_download_smoke(tmp_path: Path) -> None:
    script = ROOT / "scripts/download_pilot.sh"
    assert b"\r" not in script.read_bytes()
    subprocess.run(["/bin/bash", "-n", str(script)], timeout=10, check=True)  # noqa: S603
    destination = Path(os.environ.get("MYOSHIFT_PILOT_DESTINATION", str(tmp_path)))
    subprocess.run(  # noqa: S603
        ["/bin/bash", str(script), "--destination", str(destination)], timeout=900, check=True
    )
    assert len(list(destination.rglob("*.dat"))) == 96
    assert (destination / "SHA256SUMS.txt").exists()


def source_paths() -> list[Path]:
    """Scan public files, pruning ignored directories and build output."""
    patterns = [
        line.strip().rstrip("/")
        for line in (ROOT / ".gitignore").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    patterns.extend([".git", "build", "dist", "__pycache__"])

    def ignored(path: Path) -> bool:
        relative = path.relative_to(ROOT).as_posix()
        return any(
            fnmatch.fnmatchcase(relative if "/" in pattern else path.name, pattern)
            for pattern in patterns
        )

    paths = []
    for directory, folders, files in os.walk(ROOT, followlinks=False):
        parent = Path(directory)
        folders[:] = [name for name in folders if not ignored(parent / name)]
        paths.extend(parent / name for name in files if not ignored(parent / name))
    return paths


def tracked_paths() -> list[Path]:
    """Git handles index versions, worktrees and detached checkouts directly."""
    result = subprocess.check_output(  # noqa: S603
        ["/usr/bin/git", "ls-files", "-z"], cwd=ROOT
    )
    return [ROOT / name for name in result.decode().split("\0") if name]


def collect_text_violations(paths: list[Path]) -> list[str]:
    violations = []
    for path in sorted(paths):
        relative = path.relative_to(ROOT).as_posix()
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            continue
        if has_forbidden(relative) or has_forbidden(text):
            violations.append(relative)
    return violations


def test_public_text_hygiene() -> None:
    files = set(tracked_paths())
    files.update(source_paths())
    assert collect_text_violations(list(files)) == []


def test_public_commit_metadata_hygiene() -> None:
    result = audit_history(ROOT, os.environ.get("MYOSHIFT_AUDIT_REF", "HEAD"))
    assert result["violations"] == []


def test_frozen_protocol_canonical_bytes() -> None:
    protocol = ROOT / "docs/PREREGISTRATION.md"
    bundled = ROOT / "src/myoshift/protocol/PREREGISTRATION.md"
    expected = (ROOT / "docs/PREREGISTRATION.sha256").read_text(encoding="utf-8").strip()
    body = protocol.read_bytes()
    assert body == bundled.read_bytes()
    assert hashlib.sha256(body).hexdigest() == expected
    assert b"\r\n" in body


def test_protocol_amendment_count_matches_chronology() -> None:
    amendments = sorted((ROOT / "docs/amendments").glob("*.md"))
    from scripts.generate_report_tables import chronology

    data = json.loads((ROOT / "results/results.json").read_text())
    amendment_paths = [
        path for path in data["provenance"]["source_sha256"] if path.startswith("docs/amendments/")
    ]
    assert len(amendment_paths) == len(amendments)
    rendered = chronology(ROOT, data)
    assert len([line for line in rendered.splitlines() if line.startswith("- ")]) == len(amendments)


def test_report_supersession() -> None:
    report = (ROOT / "docs/milestones/FIX_REPORT_2026-09-30.md").read_text()
    assert "Superseded" in report and "REPAIR_2026-10-01_REPORT.md" in report
    assert "0.814" not in report


@pytest.mark.parametrize("payload", [b"12345", b"123456"])
def test_transfer_cap_boundary(tmp_path: Path, payload: bytes) -> None:
    target = tmp_path / "record.dat"
    target.write_bytes(b"original")
    response = Response(payload)
    with patch.object(DOWNLOAD.urllib.request, "urlopen", return_value=response):
        if len(payload) == 5:
            assert DOWNLOAD.fetch(DOWNLOAD.UPSTREAM + "record.dat", target, None, 5) == 5
            assert target.read_bytes() == payload
        else:
            with pytest.raises(ValueError, match="byte cap"):
                DOWNLOAD.fetch(DOWNLOAD.UPSTREAM + "record.dat", target, None, 5)
            assert target.read_bytes() == b"original"
    assert list(tmp_path.glob("*.part")) == []
