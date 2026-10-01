"""Comparison cannot hide altered scientific values or provenance."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from scripts.compare_regeneration import compare_results, compare_traces

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("change", ["metric", "provenance", "order", "extra_resource"])
def test_unlisted_regeneration_changes_fail(change: str) -> None:
    left = json.loads((ROOT / "results/results.json").read_text())
    right = copy.deepcopy(left)
    if change == "metric":
        right["runs"][0]["metrics"]["risk"]["value"] += 0.01
    elif change == "provenance":
        right["provenance"]["source_sha256"][next(iter(right["provenance"]["source_sha256"]))] = (
            "0" * 64
        )
    elif change == "order":
        right["config"]["participants"].reverse()
    else:
        right["runs"][0]["folds"][0]["runtime_s"] = 1
    with pytest.raises(ValueError):
        compare_results(left, right)


def test_only_declared_resources_may_vary() -> None:
    left = json.loads((ROOT / "results/results.json").read_text())
    right = copy.deepcopy(left)
    right["runtime_s"] += 1
    right["runs"][0]["latency_ms_p95"] += 0.01
    result = compare_results(left, right)
    assert result["allowed_resource_changes"] == ["/runs/0/latency_ms_p95", "/runtime_s"]
    assert result["exact_numeric_fields"] >= 490


def test_comparison_handles_actual_published_trace_schema(tmp_path: Path) -> None:
    first, second = tmp_path / "first.jsonl", tmp_path / "second.jsonl"
    with (ROOT / "results/predictions.jsonl").open() as trace:
        text = trace.readline() + trace.readline()
    first.write_text(text)
    second.write_text(text)
    assert compare_traces(first, second)["trace_rows"] == 2
    rows = [json.loads(line) for line in text.splitlines()]
    rows[0]["output"]["abstained"] = not rows[0]["output"]["abstained"]
    second.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    with pytest.raises(ValueError):
        compare_traces(first, second)


@pytest.mark.parametrize("difference", [0.0, 1e-13, 1e-8])
def test_trace_confidence_tolerance_is_narrow(tmp_path: Path, difference: float) -> None:
    first, second = tmp_path / "first.jsonl", tmp_path / "second.jsonl"
    first.write_text(json.dumps({"output": {"confidence": 0.4}, "participant": 44}) + "\n")
    second.write_text(
        json.dumps({"output": {"confidence": 0.4 + difference}, "participant": 44}) + "\n"
    )
    if difference > 1e-12:
        with pytest.raises(ValueError, match="tolerance"):
            compare_traces(first, second)
    else:
        assert compare_traces(first, second)["trace_rows"] == 1
