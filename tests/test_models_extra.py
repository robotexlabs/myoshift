"""Additional model tests."""

import numpy as np
import pytest

from myoshift.eval.metrics import empty_score, perfect_score, score_windows
from myoshift.features.extract import extract_window_features
from myoshift.models.lda_baseline import LdaDecoder
from myoshift.models.selective_decoder import SelectiveDecoder
from myoshift.types import StreamConfig


def test_lda_not_fitted() -> None:
    dec = LdaDecoder()
    with pytest.raises(RuntimeError):
        dec.predict(np.zeros(3))


def test_selective_independent_calibration() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=(30, 4))
    y = np.array([1, 2] * 15, dtype=np.int_)
    dec = SelectiveDecoder()
    dec.fit(x, y)
    dec.calibrate(x[:10])
    out = dec.predict(x[0])
    assert isinstance(out.abstained, bool)


def test_extract_raises_on_bad_shape() -> None:
    with pytest.raises(ValueError):
        extract_window_features(np.zeros(10), 1000)


def test_perfect_empty_dict_keys() -> None:
    assert set(perfect_score()) == set(empty_score())


def test_score_windows_length_mismatch() -> None:
    with pytest.raises(ValueError):
        score_windows([], [None])  # type: ignore[list-item]


def test_stream_config_properties() -> None:
    cfg = StreamConfig(window_ms=200, stride_ms=40)
    assert cfg.window_samples == 409
    assert cfg.stride_samples == 81
