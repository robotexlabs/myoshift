"""Split policy tests."""

import numpy as np

from myoshift.eval.splits import subject_holdout_split
from myoshift.types import WindowSample


def _ws(pid: int, sid: int) -> WindowSample:
    return WindowSample(
        features=np.zeros(3),
        label=1,
        participant_id=pid,
        session_id=sid,
        trial_key=f"p{pid}",
        time_s=0.0,
        is_rest=False,
    )


def test_subject_holdout_respects_budget() -> None:
    samples = [_ws(44, 1), _ws(44, 1), _ws(45, 1), _ws(45, 1)]
    bundle = subject_holdout_split(samples, {45}, calibration_budget=1)
    assert len(bundle.calibration) == 1
    assert len(bundle.test) == 0  # unknown support excludes the calibration record
    assert all(s.participant_id == 45 for s in bundle.test)
