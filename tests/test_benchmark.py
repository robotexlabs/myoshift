"""Integration tests for benchmark runner."""

from pathlib import Path

import numpy as np
import pytest

from myoshift.eval.benchmark import run_shift_evaluation
from myoshift.eval.dataset import build_window_samples
from myoshift.eval.metrics import bootstrap_by_trial, bootstrap_ci, score_windows
from myoshift.models.base import DecoderOutput
from myoshift.types import BudgetConfig, DecoderName, StreamConfig, WindowSample


@pytest.mark.parametrize("shift", ["person", "session", "electrode"])
def test_run_shift_evaluation(shift: str) -> None:
    root = Path("data/raw/grabmyo-flow/static_extension_WFDB")
    if not root.exists():
        pytest.skip("data not present")
    result = run_shift_evaluation(
        root,
        shift,
        DecoderName.MYOSHIFT,
        StreamConfig(),
        BudgetConfig(max_calibration_windows=10),
        test_participants=[47],
    )
    assert result["n_test"] > 0
    assert "event_recall" in result["metrics"]


def test_bootstrap_ci_bounds() -> None:
    point, low, high = bootstrap_ci([0.2, 0.3, 0.4, 0.5], n_resamples=200, seed=1)
    assert low <= point <= high


def test_bootstrap_by_trial() -> None:
    samples = [
        WindowSample(
            features=np.zeros(3),
            label=1,
            participant_id=1,
            session_id=1,
            trial_key="a",
            time_s=0.0,
            is_rest=False,
        ),
        WindowSample(
            features=np.zeros(3),
            label=1,
            participant_id=1,
            session_id=1,
            trial_key="b",
            time_s=1.0,
            is_rest=True,
        ),
    ]
    outputs = [
        DecoderOutput(gesture=1, confidence=0.9, abstained=False),
        DecoderOutput(gesture=17, confidence=0.9, abstained=False),
    ]
    metrics = bootstrap_by_trial(score_windows(samples, outputs), n_resamples=50, seed=0)
    assert "event_recall" in metrics


def test_build_window_samples_max_trials() -> None:
    root = Path("data/raw/grabmyo-flow/static_extension_WFDB")
    if not root.exists():
        pytest.skip("data not present")
    samples = build_window_samples(root, StreamConfig(), max_trials=2)
    assert len(samples) > 0


@pytest.mark.parametrize(
    "decoder",
    [DecoderName.STATIC_LDA, DecoderName.HYSTERESIS],
)
def test_decoder_variants(decoder: DecoderName) -> None:
    root = Path("data/raw/grabmyo-flow/static_extension_WFDB")
    if not root.exists():
        pytest.skip("data not present")
    result = run_shift_evaluation(
        root, "person", decoder, StreamConfig(), BudgetConfig(max_calibration_windows=50)
    )
    assert result["decoder"] == decoder.value


def test_run_full_benchmark(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = Path("data/raw/grabmyo-flow/static_extension_WFDB")
    if not root.exists():
        pytest.skip("data not present")
    from myoshift.eval.benchmark import run_full_benchmark

    root = root.resolve()
    monkeypatch.chdir(tmp_path)
    out = run_full_benchmark(root, tmp_path, StreamConfig(), BudgetConfig())
    assert len(out["runs"]) == 12
    assert (tmp_path / "results.json").exists()
