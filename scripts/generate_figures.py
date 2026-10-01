#!/usr/bin/env python3
"""Generate figures from results.json."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    results_path = ROOT / "results" / "results.json"
    if not results_path.exists():
        raise SystemExit(f"Missing {results_path}; run scripts/run_benchmark.py first")
    data = json.loads(results_path.read_text(encoding="utf-8"))
    fig_dir = ROOT / "results" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    person_runs = [
        r
        for r in data["runs"]
        if r.get("shift") == "person" and r.get("status", "available") == "available"
    ]
    decoders = sorted({r["decoder"] for r in person_runs})
    risks = []
    coverages = []
    for dec in decoders:
        run = next(r for r in person_runs if r["decoder"] == dec)
        risks.append(run["metrics"]["risk"]["value"])
        coverages.append(run["metrics"]["coverage"]["value"])

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(coverages, risks, s=80)
    for i, dec in enumerate(decoders):
        ax.annotate(dec, (coverages[i], risks[i]), textcoords="offset points", xytext=(5, 5))
    ax.set_xlabel("Coverage")
    ax.set_ylabel("Risk (error rate on non-abstained)")
    ax.set_title("Person-shift operating points (frontier untested)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(fig_dir / "risk_coverage_person.png", dpi=150)
    plt.close(fig)

    fa_rows = []
    for run in data["runs"]:
        if run.get("status", "available") != "available":
            continue
        metric = run["metrics"]["false_activations_per_rest_hour"]
        if metric["value"] is None:
            continue
        fa_rows.append(
            {
                "label": f"{run['shift']}/{run['decoder']}",
                "value": metric["value"],
                "low": metric["ci_low"] if metric["ci_low"] is not None else metric["value"],
                "high": metric["ci_high"] if metric["ci_high"] is not None else metric["value"],
                "rest_exposure_s": run.get("rest_exposure_s", 0.0),
                "false_events": run.get("false_activation_events", 0),
            }
        )
    values = [row["value"] for row in fa_rows]
    yerr = [
        [row["value"] - row["low"] for row in fa_rows],
        [row["high"] - row["value"] for row in fa_rows],
    ]
    labels = [row["label"] for row in fa_rows]

    fig2, ax2 = plt.subplots(figsize=(9, 5))
    positions = range(len(labels))
    ax2.bar(positions, values, yerr=yerr, capsize=3, color="steelblue", alpha=0.85)
    ax2.set_xticks(list(positions), labels, rotation=45, ha="right", fontsize=7)
    ax2.set_ylabel("False activations per rest hour")
    ax2.set_title("False activations by shift and decoder")
    caption_lines = [
        "Bars: point estimates with 95% participant-bootstrap intervals.",
        "Counts and rest exposure (seconds) per row:",
    ]
    for row in fa_rows:
        caption_lines.append(
            f"{row['label']}: {row['false_events']} events, {row['rest_exposure_s']:.3f} s rest"
        )
    caption_lines.append(
        "Zero-count intervals cannot establish safety equivalence; "
        "wide intervals can hide sparse exposure."
    )
    fig2.text(0.5, -0.22, "\n".join(caption_lines), ha="center", va="top", fontsize=7, wrap=True)
    fig2.tight_layout()
    fig2.savefig(fig_dir / "false_activations.png", dpi=150, bbox_inches="tight")
    plt.close(fig2)

    print(f"Figures written to {fig_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
