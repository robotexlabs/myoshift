"""Regression oracles adapted from the independent verification probes."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from click.testing import CliRunner

from myoshift.cli import main
from myoshift.data.grabmyo import load_trial_emg
from myoshift.eval import benchmark, metrics
from myoshift.eval.dataset import build_window_samples
from myoshift.eval.splits import subject_holdout_split
from myoshift.models.base import DecoderOutput
from myoshift.models.selective_decoder import SelectiveDecoder
from myoshift.types import DecoderName, StreamConfig, WindowSample

ROOT = Path("data/raw/grabmyo-flow/static_extension_WFDB")


def sample(label=17, key="rest", t=0.0, pid=1):
    return WindowSample(np.zeros(3), label, pid, 1, key, t, label == 17)


def test_f01_full_identity_mapping():
    original = [sample(g, f"p1_s1_g{g}_t1") for g in [1, 2, 3, 17]]
    shifted = [replace(s, features=np.ones(3)) for s in original]
    mapped = benchmark.map_shifted_windows(original, shifted)
    assert [(s.trial_key, s.label, s.is_rest) for s in mapped] == [
        (s.trial_key, s.label, s.is_rest) for s in original
    ]
    for invalid in [
        shifted[:-1],
        shifted + shifted[:1],
        [replace(shifted[0], label=2)] + shifted[1:],
    ]:
        with pytest.raises(ValueError):
            benchmark.map_shifted_windows(original, invalid)


def test_f02_held_event_stride_and_unavailable_exposure():
    for stride in [0.04, 0.01]:
        rest = [sample(t=i * stride) for i in range(round(5 / stride))]
        wrong = [DecoderOutput(1, 0.9, False)] * len(rest)
        scores = metrics.compute_scores(metrics.score_windows(rest, wrong))
        assert scores["false_activations_per_rest_hour"] == pytest.approx(720)
    absent = metrics.compute_scores(
        metrics.score_windows([sample(1, "gesture")], [DecoderOutput(1, 0.9, False)])
    )
    assert absent["false_activations_per_rest_hour"] is None


def test_f03_production_perfect_empty_and_ratio_counterexample():
    rest = [sample(t=i * 0.04) for i in range(125)]
    gesture = [sample(1, "gesture", i * 0.04) for i in range(125)]
    perfect = [DecoderOutput(s.label, 0.9, False) for s in rest + gesture]
    scored = metrics.score_windows(rest + gesture, perfect)
    result = metrics.bootstrap_by_trial(scored, n_resamples=50)
    assert result["event_recall"].value == 1.0
    assert result["coverage"].value == 1.0
    empty = metrics.bootstrap_by_trial(
        metrics.score_windows(rest + gesture, [DecoderOutput(1, 0.9, True)] * 250), n_resamples=50
    )
    assert empty["event_recall"].value == empty["coverage"].value == 0.0
    perfect[0] = DecoderOutput(1, 0.9, False)
    result = metrics.bootstrap_by_trial(metrics.score_windows(rest + gesture, perfect))
    assert result["false_activations_per_rest_hour"].value == pytest.approx(720)
    assert result["risk"].value == pytest.approx(1 / 250)


def test_f04_raw_support_purged_and_trial_state_reset():
    samples = build_window_samples(ROOT, StreamConfig())
    bundle = subject_holdout_split(samples, {47}, 50)
    end = bundle.calibration[-1]
    first = bundle.test[0]
    assert end.trial_key != first.trial_key or first.time_s >= end.time_s + 409 / 2048

    class Stateful:
        def __init__(self):
            self.state = 0

        def reset_state(self):
            self.state = 0

        def predict(self, x):
            self.state += 1
            return DecoderOutput(self.state, 0.9, False)

    out, _ = benchmark.predict_trials(Stateful(), [sample(1, "a"), sample(1, "b")])
    assert [o.gesture for o in out] == [1, 1]


def test_f05_participant_bootstrap_and_paired_differences():
    samples = [sample(1, f"p{p}_gesture", pid=p) for p in [1, 2]]
    a = metrics.score_windows(samples, [DecoderOutput(1, 0.9, False)] * 2)
    b = metrics.score_windows(samples, [DecoderOutput(1, 0.9, True)] * 2)
    assert metrics.bootstrap_by_participant(a)["event_recall"].value == 1.0
    delta = metrics.paired_comparison(a, b)
    assert delta["event_recall"].value == delta["event_recall"].ci_low == 1.0
    with pytest.raises(ValueError):
        metrics.paired_comparison(a, b[:-1])


def test_f06_independent_calibration_consistent_score():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(100, 6))
    y = np.repeat([1, 2], 50)
    dec = SelectiveDecoder()
    dec.fit(x, y)
    assert dec._abstain_threshold is None
    dec.calibrate(x[:10])
    confidence = np.array([dec.predict(row).confidence for row in x[:10]])
    assert dec._abstain_threshold == pytest.approx(np.quantile(1 - confidence, 0.9))
    assert dec.n_calibration == 10
    assert not hasattr(dec, "_session_mean")


def test_f07_few_shot_never_falls_back():
    rng = np.random.default_rng(1)
    x = rng.normal(size=(50, 6))
    y = np.tile([1, 2], 25)
    with pytest.raises(ValueError, match="unavailable"):
        benchmark._fit_decoder(DecoderName.FEW_SHOT, x, y, x[:10], np.full(10, 17))


def test_f08_wrist_channels_and_ring_shift():
    record = next(ROOT.rglob("*.hea")).with_suffix("")
    emg = load_trial_emg(str(record))
    assert emg.shape[1] == 12
    from myoshift.features.extract import apply_channel_shift

    x = np.arange(12, dtype=float).reshape(1, 12)
    assert apply_channel_shift(x, 2).tolist() == [[4, 5, 0, 1, 2, 3, 10, 11, 6, 7, 8, 9]]


def test_f09_generated_document_mismatch(tmp_path):
    from scripts.generate_documents import write_or_check

    path = tmp_path / "RESULTS.md"
    write_or_check(path, "from json", check=False)
    path.write_text("manual number")
    with pytest.raises(ValueError, match="mismatch"):
        write_or_check(path, "from json", check=True)


def test_f11_strict_diagnostics_and_wheel_ci():
    config = json.loads(Path("pyrightconfig.json").read_text())
    assert not any(
        config.get(k) == "none"
        for k in [
            "reportMissingImports",
            "reportUnknownMemberType",
            "reportUnknownVariableType",
            "reportUnknownArgumentType",
            "reportAttributeAccessIssue",
        ]
    )
    ci = Path(".github/workflows/ci.yml").read_text()
    assert "build --wheel" in ci and "venv" in ci and "-I" in ci


@pytest.mark.parametrize(
    "option,value", [("--stride-ms", "0"), ("--window-ms", "-1"), ("--calibration-windows", "-1")]
)
def test_f13_cli_integer_validation(option, value, monkeypatch):
    monkeypatch.setattr("myoshift.cli.run_full_benchmark", lambda *args: {"runs": []})
    result = CliRunner().invoke(main, ["benchmark", "--data-root", str(ROOT), option, value])
    assert "is not in the range" in result.output


def test_f01_real_electrode_probe():
    original = build_window_samples(ROOT, StreamConfig())
    shifted = build_window_samples(ROOT, StreamConfig(), channel_shift=2)
    mapped = benchmark.map_shifted_windows(original, shifted)
    assert len(mapped) == len(original) == len({benchmark.window_identity(s) for s in mapped})
    assert sum(s.is_rest for s in mapped) == sum(s.is_rest for s in original) > 0
    assert all(a.label == b.label for a, b in zip(original, mapped, strict=True))
    with pytest.raises(ValueError, match="duplicate"):
        benchmark.map_shifted_windows(original + original[:1], shifted)
    with pytest.raises(ValueError, match="rest flag"):
        benchmark.map_shifted_windows(
            original, [replace(shifted[0], is_rest=not shifted[0].is_rest)] + shifted[1:]
        )


def test_f02_event_offset_change_and_actual_exposure():
    rest = [replace(sample(t=i * 0.25), decision_duration_s=0.25) for i in range(8)]
    outputs = [
        DecoderOutput(g, 0.9, abstain)
        for g, abstain in [
            (1, False),
            (1, False),
            (17, False),
            (1, False),
            (2, False),
            (2, True),
            (2, False),
            (17, False),
        ]
    ]
    scored = metrics.score_windows(rest, outputs)
    assert metrics.compute_scores(scored)["false_activations_per_rest_hour"] == 4 / 2 * 3600
    assert metrics.compute_scores([])["risk"] is None
    assert metrics.bootstrap_by_trial([])["coverage"].value is None
    assert metrics.bootstrap_ci([]) == (0, 0, 0)
    one = metrics.score_windows([sample()], [DecoderOutput(1, 0.9, False)])
    assert metrics.compute_scores(one)["false_activations_per_rest_hour"] is None
    assert metrics.risk_coverage(one) == (1, 1)
    real = build_window_samples(ROOT, StreamConfig(), max_trials=1)
    exposure = sum(s.decision_duration_s for s in real)
    assert exposure == pytest.approx((10240 - 409) / 2048)
    assert real[-1].decision_duration_s < 81 / 2048


def test_f03_metric_specific_eligibility_and_wholly_abstained_trial():
    samples = [
        replace(sample(1, "correct"), decision_duration_s=0.04),
        replace(sample(2, "abstained"), decision_duration_s=0.04),
    ]
    result = metrics.bootstrap_by_trial(
        metrics.score_windows(samples, [DecoderOutput(1, 0.9, False), DecoderOutput(1, 0.9, True)])
    )
    assert result["risk"].value == 0
    assert result["event_recall"].value == 0.5
    with pytest.raises(ValueError, match="duplicate"):
        metrics.score_windows(samples[:1] * 2, [DecoderOutput(1, 0.9, False)] * 2)


def test_f04_both_split_boundaries_and_unknown_support():
    from myoshift.eval.splits import calibration_and_test, session_chrono_split

    real = build_window_samples(ROOT, StreamConfig())
    for bundle in [subject_holdout_split(real, {47}, 50), session_chrono_split(real, 3, 50)]:
        for a in bundle.calibration:
            for b in bundle.test:
                if (a.participant_id, a.session_id, a.trial_key) == (
                    b.participant_id,
                    b.session_id,
                    b.trial_key,
                ):
                    assert a.end_sample <= b.start_sample or b.end_sample <= a.start_sample
        assert len(bundle.calibration) == 50
    unknown = [sample(1, "a", 0), sample(1, "a", 1), sample(1, "b", 0)]
    assert calibration_and_test(unknown, 1)[1] == unknown[2:]
    with pytest.raises(ValueError):
        calibration_and_test(unknown, -1)


def test_f05_cluster_draws_keep_repeated_trials_and_labels():
    samples = [sample(1, f"t{i}", pid=p) for p in [1, 2] for i in range(20)]
    a = metrics.score_windows(
        samples, [DecoderOutput(1 if s.participant_id == 1 else 2, 0.9, False) for s in samples]
    )
    result = metrics.bootstrap_by_participant(a, n_resamples=200)
    assert result["event_recall"].value == 0.5
    assert (result["event_recall"].ci_low, result["event_recall"].ci_high) == (0, 1)
    delta = metrics.paired_comparison(a, a)
    assert (
        delta["event_recall"].value
        == delta["event_recall"].ci_low
        == delta["event_recall"].ci_high
        == 0
    )
    with pytest.raises(ValueError):
        metrics.paired_comparison(a, [replace(a[0], true_label=2)] + a[1:])


def test_f06_calibration_required_and_source_information_budget():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(100, 6))
    y = np.tile([1, 2], 50)
    dec = SelectiveDecoder()
    with pytest.raises(RuntimeError):
        dec.calibrate(x[:10])
    with pytest.raises(RuntimeError):
        dec.predict(x[0])
    dec.fit(x, y)
    with pytest.raises(RuntimeError, match="independently calibrated"):
        dec.predict(x[0])
    with pytest.raises(ValueError):
        dec.calibrate(x[:0])
    plain = benchmark._fit_decoder(DecoderName.STATIC_LDA, x, y, x[:10], np.full(10, 17))
    selective = benchmark._fit_decoder(DecoderName.MYOSHIFT, x, y, x[:10], np.full(10, 17))
    assert [plain.predict(row).confidence for row in x] == pytest.approx(
        [selective.predict(row).confidence for row in x]
    )
    few = benchmark._fit_decoder(DecoderName.FEW_SHOT, x, y, x[:20], y[:20])
    assert few.predict(x[0]).gesture in [1, 2]
    with pytest.raises(ValueError, match="Unknown"):
        benchmark._fit_decoder(DecoderName.SESSION_NORM, x, y, x[:10], y[:10])


def test_f08_verified_channel_names_and_invalid_ring():
    from myoshift.data.grabmyo import wrist_channel_indices
    from myoshift.features.extract import apply_channel_shift

    names = (
        ["U1"]
        + [f"W{i}" for i in range(1, 7)]
        + ["U2", "U3"]
        + [f"W{i}" for i in range(7, 13)]
        + ["U4"]
    )
    assert wrist_channel_indices(names) == list(range(1, 7)) + list(range(9, 15))
    assert wrist_channel_indices(list(reversed(names))) == [
        15 - i for i in wrist_channel_indices(names)
    ]
    for invalid in [names[:-2], names + ["W1"]]:
        with pytest.raises(ValueError):
            wrist_channel_indices(invalid)
    for x in [np.zeros(12), np.zeros((2, 16))]:
        with pytest.raises(ValueError):
            apply_channel_shift(x, 2)


def test_f13_library_integer_and_existing_runtime_budgets():
    from myoshift.data.grabmyo import iter_trial_windows
    from myoshift.types import BudgetConfig

    for kwargs in [
        {"stride_ms": 0},
        {"window_ms": 0},
        {"sample_rate_hz": -1},
        {"sample_rate_hz": 1},
    ]:
        with pytest.raises(ValueError):
            StreamConfig(**kwargs)
    with pytest.raises(ValueError):
        BudgetConfig(max_calibration_windows=-1)
    with pytest.raises(ValueError):
        list(iter_trial_windows(np.zeros((1000, 12)), 409, 0))


def test_f05_original_novelty_stop_is_retained():
    runs = []
    for shift in ["person", "session", "electrode"]:
        for decoder, bounds in [("hysteresis", (0, 100)), ("myoshift", (0, 10))]:
            runs.append(
                {
                    "shift": shift,
                    "decoder": decoder,
                    "status": "available",
                    "metrics": {
                        "false_activations_per_rest_hour": {
                            "ci_low": bounds[0],
                            "ci_high": bounds[1],
                        }
                    },
                }
            )
    assert benchmark.hysteresis_interval_stop(runs) is True
    runs[-1]["metrics"]["false_activations_per_rest_hour"] = {"ci_low": 101, "ci_high": 200}
    assert benchmark.hysteresis_interval_stop(runs) is False
    assert benchmark.hysteresis_interval_stop([]) is None


def test_f09_repair_report_links_each_numbered_amendment():
    text = Path("docs/milestones/REPAIR_2026-10-01_REPORT.md").read_text()
    row1 = next(line for line in text.splitlines() if line.startswith("| 1 |"))
    row13 = next(line for line in text.splitlines() if line.startswith("| 13 |"))
    assert "AMENDMENT_2026-10-01_01_identity_mapping.md" in row1
    assert "AMENDMENT_2026-10-01_11_integer_validation.md" in row13
