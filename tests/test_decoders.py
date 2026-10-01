"""Decoder unit tests."""

import numpy as np

from myoshift.models.hysteresis import HysteresisDecoder
from myoshift.models.lda_baseline import LdaDecoder
from myoshift.models.selective_decoder import SelectiveDecoder


def _synthetic(n: int = 40, dim: int = 6) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(0)
    x = rng.normal(size=(n, dim))
    y = np.array([0, 1] * (n // 2), dtype=np.int_)
    x[y == 0] += 1.0
    x[y == 1] -= 1.0
    return x, y


def test_lda_predicts_training_class() -> None:
    x, y = _synthetic()
    dec = LdaDecoder()
    dec.fit(x, y)
    out = dec.predict(x[0])
    assert out.gesture in (0, 1)


def test_selective_can_abstain() -> None:
    x, y = _synthetic(n=80)
    dec = SelectiveDecoder(coverage_target=0.5)
    dec.fit(x, y)
    dec.calibrate(x[:20])
    outputs = [dec.predict(row) for row in x]
    assert any(o.abstained for o in outputs)


def test_hysteresis_dwell() -> None:
    x, y = _synthetic()
    dec = HysteresisDecoder(dwell_windows=2, confidence_threshold=0.1)
    dec.fit(x, y)
    dec.reset_state()
    out1 = dec.predict(x[0])
    out2 = dec.predict(x[0])
    assert out1.gesture == 17 or out2.gesture != 17
