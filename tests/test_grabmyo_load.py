"""WFDB loading tests with local data."""

from pathlib import Path

import pytest

from myoshift.data.grabmyo import (
    discover_trials,
    is_rest_gesture,
    iter_trial_windows,
    load_trial_emg,
    parse_record_name,
)


def test_parse_record_invalid() -> None:
    assert parse_record_name("invalid.hea") is None


def test_is_rest() -> None:
    assert is_rest_gesture(17)
    assert not is_rest_gesture(1)


def test_load_trial_and_windows() -> None:
    root = Path("data/raw/grabmyo-flow/static_extension_WFDB")
    if not root.exists():
        pytest.skip("data not present")
    trials = discover_trials(root)
    emg = load_trial_emg(trials[0].emg_path)
    assert emg.ndim == 2
    windows = list(iter_trial_windows(emg, 100, 50))
    assert len(windows) > 0
    _, w = windows[0]
    assert w.shape == (100, emg.shape[1])
