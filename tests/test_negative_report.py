"""Report checks use preserved results and deliberately mismatched copies."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from scripts.generate_documents import generate as generate_documents
from scripts.generate_report_tables import ROOT, generate, render


@pytest.fixture
def report_root(tmp_path: Path) -> Path:
    paths = [
        "results/results.json",
        "docs/PREREGISTRATION.md",
        "docs/negative-result-report.md.in",
        "docs/technical-report.md",
        "CITATION.cff",
        "README.md",
    ]
    paths.extend(
        path.relative_to(ROOT).as_posix() for path in (ROOT / "docs/amendments").glob("*.md")
    )
    for relative in paths:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return tmp_path


def test_negative_report_pipeline_and_links() -> None:
    generate_documents(check=True)
    report = render()
    assert 1500 <= len(report.split()) <= 2600
    assert "docs/negative-result-report.md" in (ROOT / "README.md").read_text()
    assert "../negative-result-report.md" in (ROOT / "docs/site/index.html").read_text()


def test_negative_report_mismatch(report_root: Path) -> None:
    generate(root=report_root)
    generate(check=True, root=report_root)
    path = report_root / "docs/negative-result-report.md"
    path.write_text(path.read_text().replace("# No recall", "# Changed recall", 1))
    with pytest.raises(ValueError, match="generated document mismatch"):
        generate(check=True, root=report_root)


def test_negative_report_result_change_is_detected(report_root: Path) -> None:
    generate(root=report_root)
    path = report_root / "results/results.json"
    data = json.loads(path.read_text())
    data["runtime_s"] += 1
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="generated document mismatch"):
        generate(check=True, root=report_root)
    assert f"{data['runtime_s']:.3f} s" in render(report_root)


def test_negative_report_changed_conclusion_requires_review(report_root: Path) -> None:
    path = report_root / "results/results.json"
    data = json.loads(path.read_text())
    contrast = next(
        row for row in data["paired_comparisons"] if row["contrast"] == "myoshift minus static_lda"
    )
    contrast["metrics"]["event_recall"]["ci_high"] = 0
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="interpretation requires review"):
        render(report_root)


def test_negative_report_protocol_mismatch(report_root: Path) -> None:
    path = report_root / "docs/PREREGISTRATION.md"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="protocol hash mismatch"):
        render(report_root)


def test_negative_report_table_cell_mismatch(report_root: Path) -> None:
    generate(root=report_root)
    path = report_root / "results/results.json"
    data = json.loads(path.read_text())
    run = next(row for row in data["runs"] if row["status"] == "available")
    run["metrics"]["window_recall"]["value"] /= 2
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="generated document mismatch"):
        generate(check=True, root=report_root)
    assert f"{run['metrics']['window_recall']['value']:.3f}" in render(report_root)


def test_negative_report_amendment_mismatch(report_root: Path) -> None:
    path = next((report_root / "docs/amendments").glob("*.md"))
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="amendment hash mismatch"):
        render(report_root)
