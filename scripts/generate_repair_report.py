"""Write the repair receipt from test, command and evaluation artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from generate_documents import interval

ROOT = Path(__file__).resolve().parents[1]


def anchor(path: str, token: str) -> str:
    lines = (ROOT / path).read_text().splitlines()
    line = next(i for i, text in enumerate(lines, 1) if token in text)
    return f"`{path}:{line}`"


def main() -> None:
    data = json.loads((ROOT / "results/results.json").read_text())
    old = json.loads((ROOT / "results/historical_2026-09-30/results.json").read_text())
    rows = [
        (
            1,
            "src/myoshift/eval/benchmark.py",
            "def map_shifted_windows",
            "full_identity_mapping, real_electrode_probe",
            "Strict complete identity mapping and invariant labels/rest flags.",
        ),
        (
            2,
            "src/myoshift/eval/metrics.py",
            "def sufficient_statistics",
            "held_event_stride_and_unavailable_exposure, event_offset_change_and_actual_exposure",
            "Count command onsets; measure clipped decision exposure; missing exposure is null.",
        ),
        (
            3,
            "src/myoshift/eval/metrics.py",
            "def _bootstrap",
            "production_perfect_empty_and_ratio_counterexample, "
            "metric_specific_eligibility_and_wholly_abstained_trial",
            "Pool sufficient statistics before each metric-specific ratio.",
        ),
        (
            4,
            "src/myoshift/eval/splits.py",
            "def calibration_and_test",
            "raw_support_purged_and_trial_state_reset, both_split_boundaries_and_unknown_support",
            "Purge shared raw support and reset decoder state at independent trials.",
        ),
        (
            5,
            "src/myoshift/eval/metrics.py",
            "def bootstrap_by_participant",
            "participant_bootstrap_and_paired_differences, "
            "cluster_draws_keep_repeated_trials_and_labels",
            "All-participant hold-out folds, paired participant bootstrap, "
            "conditional/descriptive wording; frontier untested.",
        ),
        (
            6,
            "src/myoshift/models/selective_decoder.py",
            "def calibrate",
            "independent_calibration_consistent_score, "
            "calibration_required_and_source_information_budget",
            "Independent empirical calibration with consistent confidence "
            "score; cancelled normalisation removed.",
        ),
        (
            7,
            "src/myoshift/eval/benchmark.py",
            "if name == DecoderName.FEW_SHOT",
            "few_shot_never_falls_back",
            "Rest-only few-shot is unavailable, with no fallback. Equal "
            "source-informed information budgets.",
        ),
        (
            8,
            "src/myoshift/data/grabmyo.py",
            "def wrist_channel_indices",
            "wrist_channels_and_ring_shift, verified_channel_names_and_invalid_ring",
            "Named W1-W12 selection and separate within-ring permutation.",
        ),
        (
            9,
            "scripts/generate_documents.py",
            "def write_or_check",
            "generated_document_mismatch, repair_report_links_each_numbered_amendment",
            "One-command regenerated JSON, figures and current documents, with a mismatch gate.",
        ),
        (
            11,
            "src/myoshift/_external.py",
            "class WfdbAPI",
            "strict_diagnostics_and_wheel_ci",
            "Typed dependency boundaries, restored diagnostics, no unused "
            "import, isolated wheel CI steps.",
        ),
        (
            13,
            "src/myoshift/types.py",
            "def __post_init__",
            "cli_integer_validation, library_integer_and_existing_runtime_budgets",
            "Positive CLI/library dimensions and non-negative calibration "
            "budget; RSS/latency budget checks.",
        ),
    ]
    amendments = sorted((ROOT / "docs/amendments").glob("AMENDMENT_2026-10-01_[0-9][0-9]_*.md"))
    text = "# Repair report: 2026-10-01 round\n\n"
    text += (
        "All scoped regression oracles failed before repair (13 failed, "
        "`results/repair_logs/regressions_before_validated.log`), then passed after repair. "
        "Protocol changes are retrospective: results had already been seen. "
        "The filename date is the requested repair-round label, not an immutable timestamp.\n\n"
    )
    text += (
        "| Finding | Status and change | Implementation | Regression tests in "
        "tests/test_repairs.py | Amendment |\n"
    )
    text += "|---|---|---|---|---|\n"
    for item, amendment in zip(rows, amendments[: len(rows)], strict=True):
        number, path, token, tests, change = item
        test_links = ", ".join(f"`test_f{number:02}_{t.strip()}`" for t in tests.split(","))
        text += (
            f"| {number} | Fixed within scope. {change} | {anchor(path, token)} | "
            f"{test_links} | `{amendment.relative_to(ROOT)}` |\n"
        )
    text += (
        "\nAdditional anchors: "
        + ", ".join(
            [
                anchor("src/myoshift/eval/benchmark.py", "def predict_trials"),
                anchor("src/myoshift/eval/benchmark.py", "def _bundles"),
                anchor("src/myoshift/features/extract.py", "def apply_channel_shift"),
                anchor("pyrightconfig.json", "typeCheckingMode"),
                anchor(".github/workflows/ci.yml", "Build and isolated wheel install"),
                anchor("src/myoshift/cli.py", "click.IntRange"),
            ]
        )
        + ".\n"
    )
    text += "\nAdditional amendment: " + str(amendments[-1].relative_to(ROOT)) + ". "
    text += "The original conservative interval-overlap novelty stop is retained; "
    text += f"fired: {data['stop_rules']['hysteresis_interval_stop_fired']}. "
    text += "Regression: test_f05_original_novelty_stop_is_retained.\n"
    text += "\n## Old versus corrected headlines\n\n"
    text += (
        "Old event recall was a mean of per-trial window ratios, with ineligible trial zeros. "
        "It is not comparable to corrected trial-event recall. The new window-recall column "
        "makes the metric change explicit. Old person/electrode results held out one participant; "
        "the new results hold out each available participant. Original electrode labels were "
        "corrupted, so those numbers have no scientific interpretation.\n\n"
    )
    text += (
        "| Shift / method | Old reported recall [interval] | New trial-event recall [interval] | "
        "New window recall [interval] | Old n test | New n test / gesture events / participants |\n"
        "|---|---|---|---|---:|---|\n"
    )
    for run in data["runs"]:
        earlier = next(
            r for r in old["runs"] if r["shift"] == run["shift"] and r["decoder"] == run["decoder"]
        )
        text += (
            f"| {run['shift']}/{run['decoder']} | {interval(earlier['metrics']['event_recall'])} | "
        )
        if run["status"] == "unavailable":
            text += f"unavailable | unavailable | {earlier['n_test']} | unavailable |\n"
        else:
            text += (
                f"{interval(run['metrics']['event_recall'])} | "
                f"{interval(run['metrics']['window_recall'])} | {earlier['n_test']} | "
                f"{run['n_test']} / {run['n_gesture_events']} / {run['n_participants']} |\n"
            )
    text += (
        "\n| Shift / method | Old risk [interval] | New risk [interval] | Old "
        "coverage [interval] | New coverage [interval] | Old reported false/hour [interval] | "
        "New false events/hour [interval] | Rest seconds |\n"
        "|---|---|---|---|---|---|---|---:|\n"
    )
    for run in data["runs"]:
        if run["status"] != "available":
            continue
        earlier = next(
            r for r in old["runs"] if r["shift"] == run["shift"] and r["decoder"] == run["decoder"]
        )
        text += (
            f"| {run['shift']}/{run['decoder']} | "
            + " | ".join(
                [
                    interval(earlier["metrics"]["risk"]),
                    interval(run["metrics"]["risk"]),
                    interval(earlier["metrics"]["coverage"]),
                    interval(run["metrics"]["coverage"]),
                    interval(earlier["metrics"]["false_activations_per_rest_hour"]),
                    interval(run["metrics"]["false_activations_per_rest_hour"]),
                    f"{run['rest_exposure_s']:.6f}",
                ]
            )
            + " |\n"
        )
    text += (
        "\nDecoder novelty remains withdrawn. Zero-event results in some conditions "
        "and [0,0] bootstrap "
        "intervals do not establish safety equivalence. Trial-event recall is coarse and can "
        "saturate despite poor window recall. Full interpretations and paired contrasts are "
        "generated in RESULTS.md. Threshold-swept and matched-recall comparisons are untested.\n"
    )
    text += "\n## Commands and engineering gates\n\n"
    text += (
        "| Command receipt | Exact argv | Exit | Seconds | Child RSS MiB | Source changed during "
        "run | Log |\n|---|---|---:|---:|---:|---|---|\n"
    )
    for receipt in sorted((ROOT / "results/repair_logs").glob("*.json")):
        record = json.loads(receipt.read_text())
        if not isinstance(record, dict) or "argv" not in record:
            continue
        changed = record.get("source_changed_during_run", "not measured in early attempts")
        rss = record.get("child_peak_rss_mb", "unavailable")
        text += (
            f"| {record['name']} | `{json.dumps(record['argv'])}` | {record['exit']} | "
            f"{record['runtime_s']:.3f} | {rss} | {changed} | "
            f"`results/repair_logs/{record['name']}.log` |\n"
        )
    coverage = json.loads((ROOT / "results/repair_logs/coverage.json").read_text())
    text += (
        f"\nFull branch-inclusive library coverage: {coverage['totals']['percent_covered']:.2f}%.\n"
    )
    for shift in ("person", "session", "electrode"):
        for run in data["runs"]:
            if run["shift"] == shift and run["status"] == "available":
                text += (
                    f"- {shift}/{run['decoder']}: {run['runtime_s']:.3f} s; cumulative RSS "
                    f"{run['cumulative_process_peak_rss_mb']:.3f} MiB.\n"
                )
    text += (
        f"\nFull evaluation: {data['runtime_s']:.3f} s; cumulative process peak RSS "
        f"{data['cumulative_process_peak_rss_mb']:.3f} MiB. RSS includes prior folds and is "
        "not isolated per-run memory or macOS compressed/swapped footprint. Every command "
        "receipt records attempted top measurement. The sandbox rejects top, so no peak "
        "footprint claim or under-12-GB footprint certification is made. Foreground commands "
        "use recorded timeouts. No hosted CI execution is claimed.\n"
    )
    frozen = json.loads((ROOT / "results/repair_logs/frozen_before.json").read_text())
    unchanged = all(
        hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == sha for p, sha in frozen.items()
    )
    code_matches = all(
        hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == sha
        for p, sha in data["provenance"]["source_sha256"].items()
    )
    text += (
        f"\nFrozen preregistration and hash bytes unchanged: {unchanged}. "
        f"Evaluation source hashes match current files: {code_matches}. "
        "Hashes prove byte consistency only; pre-result chronology remains unverified. "
        "Source/data hashes and exact installed dependency versions are in results/results.json.\n"
    )
    text += (
        "\nDeviations: top footprint gate could not be verified because execution is denied by the "
        "sandbox. Finding 5 uses the expressly permitted untested-frontier route. Finding 7 uses "
        "the expressly permitted unavailable-baseline route. Findings 10, 12 and the downloader "
        "portion of 13 were outside the repair packet; no immutable freeze receipt, second "
        "dataset, official external controller or hosted CI run is supplied. Existing input "
        "research records remain historical source evidence. Concurrent edits were observed "
        "during early checks; affected interim runs are not final gate evidence. Final command "
        "receipts record source hashes before and after each run.\n"
    )
    if not unchanged or not code_matches:
        raise ValueError("source or frozen protocol changed after evaluation")
    (ROOT / "docs/milestones/REPAIR_2026-10-01_REPORT.md").write_text(text)


if __name__ == "__main__":
    main()
