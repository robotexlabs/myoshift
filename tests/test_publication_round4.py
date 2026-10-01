"""Publication regressions for local path redaction and historical receipts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from scripts.verify_publication import audit_history, has_forbidden

ROOT = Path(__file__).resolve().parents[1]
LOCAL_ROOTS = (b"/" + b"Users/", b"/" + b"private/", b"/" + b"var/folders/")
REDACTED_LOGS = (
    "corrected_evaluation.log",
    "regressions_before.log",
    "regressions_before_validated.log",
    "round2_full_suite.log",
    "round2_install.log",
    "round2_wheel_install.log",
    "wheel_install.log",
    "wheel_install_documented.log",
    "wheel_install_release.log",
    "wheel_install_verified.log",
)


def test_all_tracked_bytes_reject_local_paths() -> None:
    """Do not exempt logs, binary files, configuration or the test itself."""
    tracked = subprocess.check_output(  # noqa: S603
        ["/usr/bin/git", "ls-files", "-z"], cwd=ROOT
    ).split(b"\0")
    violations = []
    for name in filter(None, tracked):
        path = ROOT / name.decode()
        if any(prefix in name or prefix in path.read_bytes() for prefix in LOCAL_ROOTS):
            violations.append(name.decode())
    assert violations == [], f"machine-specific paths in tracked files: {violations}"


@pytest.mark.parametrize("prefix", LOCAL_ROOTS)
def test_history_rejects_removed_local_path(tmp_path: Path, prefix: bytes) -> None:
    def git(*args: str) -> None:
        subprocess.run(  # noqa: S603
            ["/usr/bin/git", *args], cwd=tmp_path, check=True, capture_output=True
        )

    git("init", "--initial-branch=main")
    git("config", "user.name", "Release Tester")
    git("config", "user.email", "tester@example.invalid")
    log = tmp_path / "historical.log"
    log.write_bytes(prefix + b"local-test/cache\n")
    git("add", ".")
    git("commit", "-m", "Retain historical observation")
    log.write_text("<temporary>/cache\n")
    git("add", ".")
    git("commit", "-m", "Redact historical path")
    assert audit_history(tmp_path)["violations"]


@pytest.mark.parametrize("prefix", LOCAL_ROOTS)
def test_local_path_patterns(prefix: bytes) -> None:
    assert has_forbidden(prefix.decode() + "local-test/cache")


def test_redacted_logs_identify_transformation() -> None:
    for name in REDACTED_LOGS:
        first = (ROOT / "results/repair_logs" / name).read_text().splitlines()[0]
        assert first == (
            "# Redacted publication copy: machine-specific paths replaced; "
            "recorded results unchanged."
        )


def test_historical_command_row_matches_named_receipt() -> None:
    receipt = json.loads((ROOT / "results/repair_logs/repair_report_final.json").read_text())
    report = (ROOT / "docs/milestones/REPAIR_2026-10-01_REPORT.md").read_text()
    row = next(line for line in report.splitlines() if line.startswith("| repair_report_final |"))
    cells = [cell.strip() for cell in row.split("|")[1:-1]]
    assert json.loads(cells[1].strip("`")) == receipt["argv"]
    assert int(cells[2]) == receipt["exit"]
    assert cells[3] == f"{receipt['runtime_s']:.3f}"
    assert cells[4] == str(receipt["child_peak_rss_mb"])
    assert cells[6] == "`results/repair_logs/repair_report_final.log`"
