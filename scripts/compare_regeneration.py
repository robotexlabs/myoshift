"""Compare two regenerations with a narrow, explicit resource-field allowlist."""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import zip_longest
from pathlib import Path
from typing import Any

RESOURCE_FIELDS = (
    "runtime_s",
    "cumulative_process_peak_rss_mb",
    "latency_ms_p50",
    "latency_ms_p95",
)


def resource_paths(data: dict[str, Any]) -> set[str]:
    paths = {"/runtime_s", "/cumulative_process_peak_rss_mb"}
    for index, run in enumerate(data["runs"]):
        if run["status"] == "available":
            paths.update(f"/runs/{index}/{field}" for field in RESOURCE_FIELDS)
    return paths


def compare_results(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    allowed = resource_paths(left)
    if allowed != resource_paths(right):
        raise ValueError("resource field inventory changed")
    changed: list[str] = []
    numbers = 0

    def visit(a: Any, b: Any, path: str) -> None:
        nonlocal numbers
        if path in allowed:
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise ValueError("resource value type changed: " + path)
            if a != b:
                changed.append(path)
            return
        if type(a) is not type(b):
            raise ValueError("value type changed: " + path)
        if isinstance(a, dict):
            if list(a) != list(b):
                raise ValueError("object keys or order changed: " + path)
            for key in a:
                visit(a[key], b[key], path + "/" + key)
        elif isinstance(a, list):
            if len(a) != len(b):
                raise ValueError("collection size changed: " + path)
            for index, (first, second) in enumerate(zip(a, b, strict=True)):
                visit(first, second, path + "/" + str(index))
        elif a != b:
            raise ValueError("unlisted value changed: " + path)
        elif isinstance(a, (int, float)) and not isinstance(a, bool):
            numbers += 1

    visit(left, right, "")
    return {"exact_numeric_fields": numbers, "allowed_resource_changes": changed}


def compare_traces(left: Path, right: Path) -> dict[str, Any]:
    rows = 0
    max_difference = 0.0
    with left.open() as first, right.open() as second:
        for a_line, b_line in zip_longest(first, second):
            if a_line is None or b_line is None:
                raise ValueError("trace row count changed")
            a, b = json.loads(a_line), json.loads(b_line)
            a_confidence, b_confidence = (
                a["output"].pop("confidence"),
                b["output"].pop("confidence"),
            )
            difference = abs(a_confidence - b_confidence)
            if a != b or difference > 1e-12 or round(a_confidence, 6) != round(b_confidence, 6):
                raise ValueError("trace field changed outside confidence tolerance")
            max_difference = max(max_difference, difference)
            rows += 1
    return {
        "trace_rows": rows,
        "max_confidence_difference": max_difference,
        "confidence_atol": 1e-12,
    }


def normalise_document(text: str, data: dict[str, Any], digest: str) -> str:
    text = text.replace(digest, "[RESULT_SHA256]")
    runtime, rss = data["runtime_s"], data["cumulative_process_peak_rss_mb"]
    text = text.replace(
        f"Full evaluation runtime: {runtime:.3f} s. Cumulative process peak RSS: {rss:.3f} MiB.",
        "Full evaluation runtime: [RUNTIME] s. Cumulative process peak RSS: [RSS] MiB.",
    ).replace(
        f"The preserved evaluation reports {runtime:.3f} s for benchmark runtime and "
        f"{rss:.3f} MiB for cumulative process peak RSS,",
        "The preserved evaluation reports [RUNTIME] s for benchmark runtime and "
        "[RSS] MiB for cumulative process peak RSS,",
    )
    shift = ""
    lines = []
    for line in text.splitlines(keepends=True):
        for name in ("person", "session", "electrode"):
            if line.strip() == "## " + name.capitalize() + " shift":
                shift = name
        cells = line.split("|")
        if len(cells) == 12:
            runs = [r for r in data["runs"] if r["shift"] == shift and r["status"] == "available"]
            for run in runs:
                if cells[1].strip() == run["decoder"]:
                    if cells[-2].strip() != f"{run['latency_ms_p95']:.3f}":
                        raise ValueError("document latency cell differs from its result input")
                    cells[-2] = " [P95_PREDICT] "
                    line = "|".join(cells)
        lines.append(line)
    return "".join(lines)


def compare_artifacts(first: Path, second: Path) -> dict[str, Any]:
    left_bytes = (first / "results/results.json").read_bytes()
    right_bytes = (second / "results/results.json").read_bytes()
    left, right = json.loads(left_bytes), json.loads(right_bytes)
    result = compare_results(left, right)
    result.update(
        compare_traces(first / "results/predictions.jsonl", second / "results/predictions.jsonl")
    )
    left_digest, right_digest = (
        hashlib.sha256(left_bytes).hexdigest(),
        hashlib.sha256(right_bytes).hexdigest(),
    )
    docs = [
        "README.md",
        "RESULTS.md",
        "docs/technical-report.md",
        "docs/negative-result-report.md",
        "docs/site/index.html",
    ]
    for name in docs:
        a = normalise_document((first / name).read_text(), left, left_digest)
        b = normalise_document((second / name).read_text(), right, right_digest)
        if a != b:
            raise ValueError("document changed outside named result hash/resource markers: " + name)
    figures = sorted(p.name for p in (first / "results/figures").glob("*.png"))
    if figures != sorted(p.name for p in (second / "results/figures").glob("*.png")):
        raise ValueError("figure inventory changed")
    for name in figures:
        if (first / "results/figures" / name).read_bytes() != (
            second / "results/figures" / name
        ).read_bytes():
            raise ValueError("figure bytes changed: " + name)
    return {**result, "documents_compared": docs, "byte_identical_figures": figures}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare_artifacts(args.first, args.second)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
