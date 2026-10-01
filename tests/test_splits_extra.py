"""Additional split tests."""

import numpy as np

from myoshift.eval.splits import filter_trials, session_chrono_split
from myoshift.types import TrialRecord, WindowSample


def _trial(pid: int, sid: int, gid: int) -> TrialRecord:
    return TrialRecord(pid, sid, gid, 1, "path", 12, 1000)


def test_filter_trials() -> None:
    trials = [_trial(44, 1, 1), _trial(45, 1, 17)]
    out = filter_trials(trials, participants={44})
    assert len(out) == 1


def test_session_chrono_split() -> None:
    samples = [
        WindowSample(np.zeros(2), 1, 44, 1, "k", 0.0, False),
        WindowSample(np.zeros(2), 1, 44, 3, "k2", 0.0, False),
    ]
    bundle = session_chrono_split(samples, test_session=3, calibration_budget=1)
    assert bundle.shift_type.value == "session"
