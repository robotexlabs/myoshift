"""Generate the negative-result report without rerunning or altering pilot results.

Measurements come exclusively from results/results.json. Bibliographic identifiers,
licence identifiers and dated verification labels come from their repository sources.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from string import Template
from typing import Any

import yaml

try:
    from scripts.generate_documents import interval, tables, write_or_check
except ModuleNotFoundError:
    from generate_documents import interval, tables, write_or_check

ROOT = Path(__file__).resolve().parents[1]


def chronology(root: Path, data: dict[str, Any]) -> str:
    summaries = (
        "Withdrawn aggregate historical repair note; superseded by the separate repair ledger.",
        "Require complete window identity and unchanged labels in shifted-data mapping.",
        "Count command onsets and measured rest exposure; distinguish trial and window recall.",
        "Pool sufficient statistics before ratios; preserve undefined estimates as unavailable.",
        "Purge overlapping raw support and reset decoder state at record boundaries.",
        "Use all participant hold-outs and paired participant uncertainty; frontier untested.",
        "Use independent empirical calibration; remove cancelled normalisation and guarantees.",
        "Remove few-shot fallback and state source-information budgets explicitly.",
        "Select named wrist channels and permute within each ring as a displacement proxy.",
        "Generate current reporting from results with mismatch checks and provenance.",
        "Restore strict typing diagnostics and isolated wheel verification.",
        "Validate dimensions and budgets; keep resource-measurement limitations explicit.",
        "Retain the conservative novelty withdrawal stop; overlap is not safety equivalence.",
        "Reconcile the stricter resource cap; footprint compliance remains unverified.",
        "Pin CRLF protocol bytes in Git and record the LF checkout correction.",
    )
    paths = sorted(
        path for path in data["provenance"]["source_sha256"] if path.startswith("docs/amendments/")
    )
    if len(paths) != len(summaries):
        raise ValueError("amendment ledger changed; review chronology summaries")
    lines = []
    for path, summary in zip(paths, summaries, strict=True):
        amendment = root / path
        if hashlib.sha256(amendment.read_bytes()).hexdigest() != (
            data["provenance"]["source_sha256"][path]
        ):
            raise ValueError("amendment hash mismatch")
        source = amendment.read_text()
        date = re.search(r"\d{4}-\d{2}-\d{2}", Path(path).name)
        if date is None:
            raise ValueError("missing amendment date")
        finding = re.search(r"Verification findings?[^\n]*", source)
        labels = re.findall(r"\d+", finding.group()) if finding else []
        label = f"; verification finding(s) {', '.join(labels)}" if labels else ""
        title = source.split("\n")[0].removeprefix("# ")
        if title.startswith(">"):
            title = "Withdrawn aggregate note"
        lines.append(f"- {date.group()}{label}: [{title}]({path.removeprefix('docs/')}). {summary}")
    return "\n".join(lines)


def render(root: Path = ROOT) -> str:
    source = root / "results/results.json"
    data = json.loads(source.read_text())
    config = data["config"]
    protocol_hash = data["provenance"]["protocol_sha256"]
    if hashlib.sha256((root / "docs/PREREGISTRATION.md").read_bytes()).hexdigest() != protocol_hash:
        raise ValueError("protocol hash mismatch")
    citation = yaml.safe_load((root / "CITATION.cff").read_text())
    readme = (root / "README.md").read_text()
    technical = (root / "docs/technical-report.md").read_text()
    dataset_doi = re.search(r"https://doi.org/10\.13026/[^)]+", technical)
    related_doi = re.search(r"https://doi.org/10\.1038/[^)]+", readme)
    arxiv = re.search(r"https://arxiv.org/abs/[^)]+", readme)
    licence = re.search(r"CC BY [\d.]+", readme)
    if not (dataset_doi and related_doi and arxiv and licence):
        raise ValueError("missing repository reference or licence")
    for row in data["paired_comparisons"]:
        if row["contrast"] != "myoshift minus static_lda":
            continue
        for metric in ("event_recall", "window_recall"):
            if row["metrics"][metric]["ci_high"] >= 0:
                raise ValueError("negative-result interpretation requires review")
    if not data["stop_rules"]["hysteresis_interval_stop_fired"]:
        raise ValueError("novelty-stop interpretation requires review")
    contrasts = {
        row["shift"]: interval(row["metrics"]["event_recall"])
        for row in data["paired_comparisons"]
        if row["contrast"] == "myoshift minus static_lda"
    }
    rest = config["stream"]["rest_gesture_id"]
    events = sum(
        name.endswith(".hea") and f"_gesture{rest}_" not in name
        for name in data["provenance"]["data_sha256"]
    )
    author = citation["authors"][0]
    values = {
        "participants": str(len(config["participants"])),
        "records": str(config["n_records"]),
        "windows": str(config["n_windows"]),
        "events": str(events),
        "licence": licence.group(),
        "dataset_doi": dataset_doi.group(),
        "related_doi": related_doi.group(),
        "arxiv": arxiv.group(),
        "abstract_contrasts": "; ".join(f"{shift}: {value}" for shift, value in contrasts.items()),
        "protocol_hash": protocol_hash,
        "results_hash": hashlib.sha256(source.read_bytes()).hexdigest(),
        "chronology": chronology(root, data),
        "tables": tables(data),
        "window_ms": str(config["stream"]["window_ms"]),
        "stride_ms": str(config["stream"]["stride_ms"]),
        "sample_rate": str(config["stream"]["sample_rate_hz"]),
        "features": str(config["feature_dimensions"]),
        "calibration": str(config["budget"]["max_calibration_windows"]),
        "runtime": f"{data['runtime_s']:.3f}",
        "rss": f"{data['cumulative_process_peak_rss_mb']:.3f}",
        "python": data["provenance"]["python"],
        "software": json.dumps(data["provenance"]["software"], sort_keys=True),
        "author": f"{author['family-names']}, {author['given-names']}",
        "citation_title": citation["title"],
        "version": citation["version"],
        "released": str(citation["date-released"]),
        "code_licence": citation["license"],
        "repository": citation["repository-code"],
        "novelty_stop": str(data["stop_rules"]["hysteresis_interval_stop_fired"]),
        "coverage_stop": str(data["stop_rules"]["person_coverage_failure"]),
    }
    template = (root / "docs/negative-result-report.md.in").read_text()
    return Template(template).substitute(values)


def generate(*, check: bool = False, root: Path = ROOT) -> None:
    write_or_check(root / "docs/negative-result-report.md", render(root), check=check)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    generate(check=parser.parse_args().check)
