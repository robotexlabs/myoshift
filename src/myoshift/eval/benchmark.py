"""Real-data evaluations with identity checks and paired participant uncertainty."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np

from myoshift.eval.dataset import build_window_samples
from myoshift.eval.metrics import (
    ScoredWindow,
    bootstrap_by_participant,
    paired_comparison,
    score_windows,
    sufficient_statistics,
)
from myoshift.eval.splits import SplitBundle, session_chrono_split, subject_holdout_split
from myoshift.models.base import Decoder, DecoderOutput
from myoshift.models.hysteresis import HysteresisDecoder
from myoshift.models.lda_baseline import LdaDecoder
from myoshift.models.selective_decoder import SelectiveDecoder
from myoshift.types import (
    BudgetConfig,
    DecoderName,
    FloatArray,
    IntArray,
    StreamConfig,
    WindowSample,
)


def _peak_rss_mb() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return usage / (1024 * 1024) if sys.platform == "darwin" else usage / 1024


def _fit_decoder(
    name: DecoderName,
    train_x: FloatArray,
    train_y: IntArray,
    calib_x: FloatArray,
    calib_y: IntArray,
) -> Decoder:
    if name == DecoderName.FEW_SHOT:
        if len(np.unique(calib_y)) < 2:
            raise ValueError("few_shot baseline unavailable: calibration lacks two classes")
        few_shot = LdaDecoder()
        few_shot.fit(calib_x, calib_y)
        return few_shot
    if name == DecoderName.STATIC_LDA:
        decoder: Decoder = LdaDecoder()
    elif name == DecoderName.HYSTERESIS:
        decoder = HysteresisDecoder()
    elif name == DecoderName.MYOSHIFT:
        selective = SelectiveDecoder()
        selective.fit(train_x, train_y)
        selective.calibrate(calib_x)
        return selective
    else:
        raise ValueError(f"Unknown decoder: {name}")
    decoder.fit(train_x, train_y)
    return decoder


def window_identity(sample: WindowSample) -> tuple[int, int, str, float, int | None, int | None]:
    return (
        sample.participant_id,
        sample.session_id,
        sample.trial_key,
        sample.time_s,
        sample.start_sample,
        sample.end_sample,
    )


def map_shifted_windows(
    original: list[WindowSample],
    shifted: list[WindowSample],
) -> list[WindowSample]:
    """Require a complete one-to-one identity mapping, without any fallback."""
    lookup = {window_identity(s): s for s in shifted}
    original_keys = [window_identity(s) for s in original]
    if len(lookup) != len(shifted) or len(set(original_keys)) != len(original):
        raise ValueError("duplicate window identity in electrode mapping")
    if set(original_keys) != set(lookup):
        raise ValueError("missing or extra window identity in electrode mapping")
    mapped = [lookup[key] for key in original_keys]
    for a, b in zip(original, mapped, strict=True):
        same = (
            a.label,
            a.is_rest,
            a.decision_duration_s,
        ) == (b.label, b.is_rest, b.decision_duration_s)
        if not same:
            raise ValueError("electrode mapping changed label, rest flag or exposure")
    return mapped


def _footprint_measurement_status() -> str:
    try:
        subprocess.run(  # noqa: S603
            ["/usr/bin/top", "-l", "1", "-pid", str(os.getpid()), "-stats", "pid,mem"],
            capture_output=True,
            timeout=5,
            check=True,
        )
        return "attempted"
    except (OSError, subprocess.SubprocessError):
        return "blocked or unavailable"


def predict_trials(
    decoder: Decoder,
    samples: list[WindowSample],
) -> tuple[list[DecoderOutput], list[float]]:
    outputs: list[DecoderOutput] = []
    latencies: list[float] = []
    previous: tuple[int, int, str] | None = None
    for sample in samples:
        key = (sample.participant_id, sample.session_id, sample.trial_key)
        if key != previous:
            decoder.reset_state()
        previous = key
        start = time.perf_counter()
        outputs.append(decoder.predict(sample.features))
        latencies.append((time.perf_counter() - start) * 1000)
    return outputs, latencies


def _bundles(
    samples: list[WindowSample],
    shift: str,
    budget: BudgetConfig,
    test_participants: list[int] | None,
    test_session: int,
    shifted: list[WindowSample] | None,
) -> list[SplitBundle]:
    if shift == "session":
        return [session_chrono_split(samples, test_session, budget.max_calibration_windows)]
    if shift not in ("person", "electrode"):
        raise ValueError(f"Unknown shift: {shift}")
    participants = test_participants or sorted({s.participant_id for s in samples})
    mapped = map_shifted_windows(samples, shifted) if shifted is not None else samples
    mapped_lookup = {window_identity(s): s for s in mapped}
    bundles: list[SplitBundle] = []
    for pid in participants:
        bundle = subject_holdout_split(samples, {pid}, budget.max_calibration_windows)
        if shifted is not None:
            bundle = SplitBundle(
                bundle.train,
                bundle.calibration,
                [mapped_lookup[window_identity(s)] for s in bundle.test],
                bundle.shift_type,
                f"participant:{pid};within_ring_shift:2",
            )
        bundles.append(bundle)
    return bundles


def _evaluate(
    samples: list[WindowSample],
    shift: str,
    decoder_name: DecoderName,
    budget: BudgetConfig,
    test_participants: list[int] | None = None,
    test_session: int = 3,
    shifted: list[WindowSample] | None = None,
    seed: int = 42,
) -> tuple[dict[str, Any], list[ScoredWindow]]:
    started = time.perf_counter()
    bundles = _bundles(samples, shift, budget, test_participants, test_session, shifted)
    scored: list[ScoredWindow] = []
    latencies: list[float] = []
    folds: list[dict[str, Any]] = []
    for bundle in bundles:
        if not bundle.train or not bundle.test:
            raise ValueError("empty training or test partition")
        train_x = np.vstack([s.features for s in bundle.train])
        train_y = np.asarray([s.label for s in bundle.train], dtype=np.int_)
        calib_x = (
            np.vstack([s.features for s in bundle.calibration])
            if bundle.calibration
            else np.empty((0, train_x.shape[1]), dtype=np.float64)
        )
        calib_y = np.asarray([s.label for s in bundle.calibration], dtype=np.int_)
        test_pids = {t.participant_id for t in bundle.test}
        test_sessions = {t.session_id for t in bundle.test}
        fold: dict[str, Any] = {
            "held_out": bundle.held_out,
            "n_train": len(bundle.train),
            "n_calibration": len(bundle.calibration),
            "n_test": len(bundle.test),
            "calibration_labels": sorted(set(calib_y.tolist())),
            "n_purged": sum(
                s.participant_id in test_pids and s.session_id in test_sessions for s in samples
            )
            - len(bundle.calibration)
            - len(bundle.test),
        }
        try:
            decoder = _fit_decoder(decoder_name, train_x, train_y, calib_x, calib_y)
        except ValueError as exc:
            if decoder_name not in (DecoderName.FEW_SHOT, DecoderName.MYOSHIFT):
                raise
            return {
                "shift": shift,
                "decoder": decoder_name.value,
                "status": "unavailable",
                "reason": str(exc),
                "folds": [fold],
                "metrics": {},
            }, []
        outputs, times = predict_trials(decoder, bundle.test)
        scored.extend(score_windows(bundle.test, outputs))
        latencies.extend(times)
        if isinstance(decoder, SelectiveDecoder):
            fold["threshold_examples"] = decoder.n_calibration
            fold["confidence_score_threshold"] = decoder.score_threshold
        folds.append(fold)
        if _peak_rss_mb() > budget.max_peak_ram_mb:
            raise RuntimeError("RSS budget exceeded")
    metrics = bootstrap_by_participant(scored, seed=seed)
    p95 = float(np.quantile(latencies, 0.95))
    if p95 > budget.max_inference_ms_p95:
        raise RuntimeError("inference latency budget exceeded")
    stats = sufficient_statistics(scored)
    participants = sorted({s.participant_id for s in scored})
    return {
        "shift": shift,
        "decoder": decoder_name.value,
        "status": "available",
        "held_out": [f["held_out"] for f in folds],
        "folds": folds,
        "n_train": sum(f["n_train"] for f in folds),
        "n_calibration": sum(f["n_calibration"] for f in folds),
        "n_test": len(scored),
        "n_participants": len(participants),
        "n_trials": len({s.identity[:3] for s in scored}),
        "n_gesture_events": int(stats[3]),
        "n_gesture_windows": int(stats[5]),
        "false_activation_events": int(stats[0]),
        "rest_exposure_s": float(stats[1]),
        "interval_scope": (
            "participant-cluster descriptive pilot intervals; shared training folds"
            if len(participants) > 1
            else "conditional on one held-out participant"
        ),
        "metrics": {k: asdict(v) for k, v in metrics.items()},
        "latency_ms_p50": float(np.quantile(latencies, 0.5)),
        "latency_ms_p95": p95,
        "runtime_s": time.perf_counter() - started,
        "cumulative_process_peak_rss_mb": _peak_rss_mb(),
    }, scored


def run_shift_evaluation(
    data_root: Path,
    shift: str,
    decoder_name: DecoderName,
    stream_config: StreamConfig,
    budget: BudgetConfig,
    test_participants: list[int] | None = None,
    test_session: int = 3,
    channel_shift: int = 0,
    seed: int = 42,
) -> dict[str, Any]:
    samples = build_window_samples(data_root, stream_config)
    if not samples:
        raise ValueError(f"No samples found under {data_root}")
    shifted = (
        build_window_samples(data_root, stream_config, channel_shift=channel_shift or 2)
        if shift == "electrode"
        else None
    )
    result, _ = _evaluate(
        samples, shift, decoder_name, budget, test_participants, test_session, shifted, seed
    )
    return result


def hysteresis_interval_stop(runs: list[dict[str, Any]]) -> bool | None:
    """Conservative registered novelty stop: overlapping intervals on every shift.

    This is a withdrawal decision, never an equivalence or superiority test.
    """
    for shift in ("person", "session", "electrode"):
        methods = {r["decoder"]: r for r in runs if r["shift"] == shift}
        bounds: list[tuple[float, float]] = []
        for name in ("hysteresis", "myoshift"):
            run = methods.get(name)
            if run is None or run["status"] != "available":
                return None
            metric = run["metrics"]["false_activations_per_rest_hour"]
            if metric["ci_low"] is None or metric["ci_high"] is None:
                return None
            bounds.append((metric["ci_low"], metric["ci_high"]))
        if max(b[0] for b in bounds) > min(b[1] for b in bounds):
            return False
    return True


def run_full_benchmark(
    data_root: Path,
    output_dir: Path,
    stream_config: StreamConfig | None = None,
    budget: BudgetConfig | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    stream_config, budget = stream_config or StreamConfig(), budget or BudgetConfig()
    package_root = Path(__file__).resolve().parents[1]
    checkout_root = package_root.parents[1]
    if (checkout_root / "pyproject.toml").is_file():
        provenance_root = checkout_root
        protocol_path = checkout_root / "docs/PREREGISTRATION.md"
    else:
        provenance_root = package_root
        protocol_path = package_root / "protocol/PREREGISTRATION.md"
    protocol_sha = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    software = {name: version(name) for name in ("myoshift", "numpy", "scikit-learn", "wfdb")}
    from myoshift.provenance import hashes, source_files

    source_sha = hashes(provenance_root, source_files(provenance_root))
    samples = build_window_samples(data_root, stream_config)
    if not samples:
        raise ValueError(f"No samples found under {data_root}")
    shifted = build_window_samples(data_root, stream_config, channel_shift=2)
    map_shifted_windows(samples, shifted)
    data_sha = {
        str(path.relative_to(data_root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(data_root.rglob("*"))
        if path.suffix in (".hea", ".dat")
    }
    results: dict[str, Any] = {
        "schema_version": 2,
        "provenance": {
            "protocol_sha256": protocol_sha,
            "freeze_chronology": "unverified; amendments made after results were seen",
            "software": software,
            "python": platform.python_version(),
            "hardware": platform.machine(),
            "hostname": platform.node(),
            "platform": platform.platform(),
            "footprint_measurement": _footprint_measurement_status(),
            "latency_scope": (
                "decoder.predict call only; excludes feature extraction, acquisition "
                "and end-to-end command response"
            ),
            "source_sha256": source_sha,
            "data_sha256": data_sha,
        },
        "config": {
            "stream": asdict(stream_config),
            "budget": asdict(budget),
            "participants": sorted({s.participant_id for s in samples}),
            "n_records": len({s.trial_key for s in samples}),
            "n_windows": len(samples),
            "feature_dimensions": len(samples[0].features),
        },
        "comparison_scope": "threshold-swept risk-coverage and matched-recall comparison untested",
        "runs": [],
        "paired_comparisons": [],
    }
    predictions: dict[str, dict[str, list[ScoredWindow]]] = {}
    for shift in ("person", "session", "electrode"):
        predictions[shift] = {}
        for name in (
            DecoderName.STATIC_LDA,
            DecoderName.HYSTERESIS,
            DecoderName.FEW_SHOT,
            DecoderName.MYOSHIFT,
        ):
            run, scored = _evaluate(
                samples, shift, name, budget, shifted=shifted if shift == "electrode" else None
            )
            results["runs"].append(run)
            predictions[shift][name.value] = scored
            print(f"{shift}/{name.value}: {run['status']}", flush=True)
        for baseline in (DecoderName.STATIC_LDA, DecoderName.HYSTERESIS):
            left, right = predictions[shift]["myoshift"], predictions[shift][baseline.value]
            results["paired_comparisons"].append(
                {
                    "shift": shift,
                    "contrast": f"myoshift minus {baseline.value}",
                    "status": "available" if left and right else "unavailable",
                    "metrics": {k: asdict(v) for k, v in paired_comparison(left, right).items()}
                    if left and right
                    else {},
                }
            )
    person = next(
        r for r in results["runs"] if r["shift"] == "person" and r["decoder"] == "myoshift"
    )
    coverage_value = person["metrics"].get("coverage", {}).get("value")
    results["stop_rules"] = {
        "person_coverage_failure": coverage_value < budget.abstention_coverage_min
        if coverage_value is not None
        else None,
        "hysteresis_interval_stop_fired": hysteresis_interval_stop(results["runs"]),
        "decoder_novelty_claim": "withdrawn; overlapping intervals are not safety equivalence",
        "threshold_frontier": "untested",
    }
    results["runtime_s"] = time.perf_counter() - started
    results["cumulative_process_peak_rss_mb"] = _peak_rss_mb()
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "results.json"
    results_path.write_text(
        json.dumps(results, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    with (output_dir / "predictions.jsonl").open("w", encoding="utf-8") as handle:
        for shift, methods in predictions.items():
            for method_name, scored in methods.items():
                for s in scored:
                    handle.write(
                        json.dumps({"shift": shift, "decoder": method_name, **asdict(s)}) + "\n"
                    )
    return results
