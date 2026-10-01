"""Causal feature extraction for streaming windows."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def bandpower(window: NDArray[np.floating], sample_rate_hz: int) -> float:
    spectrum = np.abs(np.fft.rfft(window - window.mean()))
    freqs = np.fft.rfftfreq(len(window), d=1.0 / sample_rate_hz)
    mask = (freqs >= 20.0) & (freqs <= 450.0)
    return float(np.sum(spectrum[mask] ** 2))


def extract_window_features(
    window: NDArray[np.floating],
    sample_rate_hz: int,
) -> NDArray[np.float64]:
    """Extract per-channel MAV, RMS and bandpower (3 * n_channels features)."""
    if window.ndim != 2:
        raise ValueError("window must be (n_samples, n_channels)")
    mav = np.mean(np.abs(window), axis=0)
    rms = np.sqrt(np.mean(window**2, axis=0))
    bp = np.array(
        [bandpower(window[:, ch], sample_rate_hz) for ch in range(window.shape[1])],
        dtype=np.float64,
    )
    return np.concatenate([mav, rms, bp]).astype(np.float64)


def apply_channel_shift(emg: NDArray[np.floating], shift: int) -> NDArray[np.floating]:
    """Cyclic channel permutation to simulate electrode displacement."""
    if emg.ndim != 2:
        raise ValueError("emg must be 2-D")
    if emg.shape[1] != 12:
        raise ValueError("within-ring shift requires 12 wrist channels")
    return np.concatenate(
        [
            np.roll(emg[:, :6], shift % 6, axis=1),
            np.roll(emg[:, 6:], shift % 6, axis=1),
        ],
        axis=1,
    )
