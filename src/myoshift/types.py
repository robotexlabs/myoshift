"""Shared type definitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.floating]
IntArray = NDArray[np.int_]

REST_GESTURE_ID = 17


class ShiftType(StrEnum):
    PERSON = "person"
    SESSION = "session"
    ELECTRODE = "electrode"


class DecoderName(StrEnum):
    STATIC_LDA = "static_lda"
    SESSION_NORM = "session_norm"
    FEW_SHOT = "few_shot"
    HYSTERESIS = "hysteresis"
    MYOSHIFT = "myoshift"


@dataclass(frozen=True)
class StreamConfig:
    sample_rate_hz: int = 2048
    window_ms: int = 200
    stride_ms: int = 40
    rest_gesture_id: int = REST_GESTURE_ID

    def __post_init__(self) -> None:
        if min(self.sample_rate_hz, self.window_ms, self.stride_ms) <= 0:
            raise ValueError("sample rate, window and stride must be positive")
        if min(self.window_samples, self.stride_samples) < 1:
            raise ValueError("window and stride must each contain at least one sample")

    @property
    def window_samples(self) -> int:
        return int(self.sample_rate_hz * self.window_ms / 1000)

    @property
    def stride_samples(self) -> int:
        return int(self.sample_rate_hz * self.stride_ms / 1000)


@dataclass(frozen=True)
class BudgetConfig:
    """Deployment compute and calibration budget."""

    max_calibration_windows: int = 50
    max_inference_ms_p95: float = 50.0
    max_peak_ram_mb: float = 2048.0
    abstention_coverage_min: float = 0.05

    def __post_init__(self) -> None:
        if self.max_calibration_windows < 0:
            raise ValueError("calibration budget must be non-negative")


@dataclass(frozen=True)
class TrialRecord:
    participant_id: int
    session_id: int
    gesture_id: int
    trial_id: int
    emg_path: str
    n_channels: int
    n_samples: int


@dataclass(frozen=True)
class WindowSample:
    features: FloatArray
    label: int
    participant_id: int
    session_id: int
    trial_key: str
    time_s: float
    is_rest: bool
    start_sample: int | None = None
    end_sample: int | None = None
    decision_duration_s: float | None = None


@dataclass(frozen=True)
class EventPrediction:
    time_s: float
    predicted_gesture: int
    confidence: float
    abstained: bool


@dataclass(frozen=True)
class MetricResult:
    name: str
    value: float | None
    ci_low: float | None
    ci_high: float | None
    unit: str


SplitPolicy = Literal["subject_holdout", "session_chrono", "electrode_shift"]
