"""Tests for scoring metrics."""

import numpy as np

from myoshift.eval.metrics import (
    compute_scores,
    perfect_score,
    score_windows,
)
from myoshift.models.base import DecoderOutput
from myoshift.types import REST_GESTURE_ID, WindowSample


def _sample(label: int, is_rest: bool, key: str, t: float) -> WindowSample:
    return WindowSample(
        features=np.zeros(6),
        label=label,
        participant_id=44,
        session_id=1,
        trial_key=key,
        time_s=t,
        is_rest=is_rest,
        decision_duration_s=0.04,
    )


def test_perfect_scorer_scores_one() -> None:
    samples = [
        _sample(1, False, "t1", 0.0),
        _sample(REST_GESTURE_ID, True, "t2", 1.0),
    ]
    outputs = [
        DecoderOutput(gesture=1, confidence=0.95, abstained=False),
        DecoderOutput(gesture=REST_GESTURE_ID, confidence=0.95, abstained=False),
    ]
    scores = compute_scores(score_windows(samples, outputs))
    for key, expected in perfect_score().items():
        got = scores[key]
        if expected is None:
            assert got is None
        else:
            assert abs(float(got) - float(expected)) < 1e-9


def test_empty_scorer_scores_zero_recall() -> None:
    samples = [_sample(1, False, "t1", 0.0)]
    outputs = [DecoderOutput(gesture=2, confidence=0.9, abstained=False)]
    scores = compute_scores(score_windows(samples, outputs))
    assert scores["event_recall"] == 0.0
    assert scores["risk"] == 1.0
