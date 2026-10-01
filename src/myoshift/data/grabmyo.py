"""GRABMyoFlow WFDB loader with streaming access."""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

import numpy as np

from myoshift._external import wfdb
from myoshift.types import REST_GESTURE_ID, FloatArray, TrialRecord

_RECORD_RE = re.compile(r"session(\d+)_participant(\d+)_gesture(\d+)_trial(\d+)\.(?:hea|dat)$")


def parse_record_name(name: str) -> tuple[int, int, int, int] | None:
    match = _RECORD_RE.match(name)
    if match is None:
        return None
    groups = match.groups()
    return (int(groups[0]), int(groups[1]), int(groups[2]), int(groups[3]))


def discover_trials(data_root: Path) -> list[TrialRecord]:
    """Discover WFDB trial records under a GRABMyoFlow static tree."""
    trials: list[TrialRecord] = []
    for hea_path in sorted(data_root.rglob("*.hea")):
        parsed = parse_record_name(hea_path.name)
        if parsed is None:
            continue
        session_id, participant_id, gesture_id, trial_id = parsed
        dat_path = hea_path.with_suffix(".dat")
        if not dat_path.exists():
            continue
        header = wfdb.rdheader(str(hea_path.with_suffix("")))
        trials.append(
            TrialRecord(
                participant_id=participant_id,
                session_id=session_id,
                gesture_id=gesture_id,
                trial_id=trial_id,
                emg_path=str(hea_path.with_suffix("")),
                n_channels=header.n_sig,
                n_samples=header.sig_len,
            )
        )
    return trials


def load_trial_emg(record_path: str) -> FloatArray:
    """Load one trial as (n_samples, n_channels) float64 in millivolts."""
    record = wfdb.rdrecord(record_path, physical=True)
    raw_signal = getattr(record, "p_signal", None)
    if raw_signal is None:
        raise ValueError(f"No physical signal in record {record_path}")
    signals = np.asarray(raw_signal, dtype=np.float64)
    if signals.ndim != 2:
        raise ValueError(f"Expected 2-D signal, got shape {signals.shape}")
    names = record.sig_name
    indices = wrist_channel_indices(names)
    return signals[:, indices]


def iter_trial_windows(
    emg: FloatArray,
    window_samples: int,
    stride_samples: int,
) -> Iterator[tuple[int, FloatArray]]:
    """Yield (start_index, window) pairs causally along a trial."""
    if window_samples <= 0 or stride_samples <= 0:
        raise ValueError("window and stride must be positive")
    n_samples = emg.shape[0]
    start = 0
    while start + window_samples <= n_samples:
        yield start, emg[start : start + window_samples]
        start += stride_samples


def is_rest_gesture(gesture_id: int) -> bool:
    return gesture_id == REST_GESTURE_ID


def wrist_channel_indices(names: list[str]) -> list[int]:
    """Select W1-W12 in ring order, rejecting missing or duplicate names."""
    expected = [f"W{i}" for i in range(1, 13)]
    if any(names.count(name) != 1 for name in expected):
        raise ValueError("Missing or duplicate wrist channel names")
    return [names.index(name) for name in expected]
