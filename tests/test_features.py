"""Feature extraction tests."""

import numpy as np

from myoshift.features.extract import apply_channel_shift, extract_window_features


def test_channel_shift_is_cyclic() -> None:
    emg = np.arange(48, dtype=np.float64).reshape(4, 12)
    shifted = apply_channel_shift(emg, 1)
    assert shifted.shape == emg.shape
    assert np.allclose(shifted[:, 0], emg[:, 5])
    assert np.allclose(shifted[:, 6], emg[:, 11])


def test_extract_window_features_length() -> None:
    window = np.random.randn(200, 4)
    feats = extract_window_features(window, sample_rate_hz=1000)
    assert feats.shape == (12,)
