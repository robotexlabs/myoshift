"""Threshold and hysteresis event decoder wrapping an LDA."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from myoshift.models.base import Decoder, DecoderOutput
from myoshift.models.lda_baseline import LdaDecoder
from myoshift.types import REST_GESTURE_ID


class HysteresisDecoder(Decoder):
    """LDA with confidence threshold, dwell time and rest mapping."""

    def __init__(
        self,
        confidence_threshold: float = 0.55,
        dwell_windows: int = 3,
        rest_gesture_id: int = REST_GESTURE_ID,
    ) -> None:
        self._inner = LdaDecoder(rest_gesture_id=rest_gesture_id)
        self._confidence_threshold = confidence_threshold
        self._dwell_windows = dwell_windows
        self._rest_gesture_id = rest_gesture_id
        self._pending_gesture: int | None = None
        self._pending_count: int = 0
        self._committed_gesture: int = rest_gesture_id

    def fit(self, x: NDArray[np.floating], y: NDArray[np.int_]) -> None:
        self._inner.fit(x, y)
        self.reset_state()

    def reset_state(self) -> None:
        self._pending_gesture = None
        self._pending_count = 0
        self._committed_gesture = self._rest_gesture_id

    def predict(self, x: NDArray[np.floating]) -> DecoderOutput:
        raw = self._inner.predict(x)
        if raw.confidence < self._confidence_threshold:
            self._pending_gesture = None
            self._pending_count = 0
            self._committed_gesture = self._rest_gesture_id
            return DecoderOutput(
                gesture=self._rest_gesture_id,
                confidence=raw.confidence,
                abstained=False,
            )
        if raw.gesture == self._rest_gesture_id:
            self._pending_gesture = None
            self._pending_count = 0
            self._committed_gesture = self._rest_gesture_id
            return DecoderOutput(
                gesture=self._rest_gesture_id,
                confidence=raw.confidence,
                abstained=False,
            )
        if raw.gesture == self._pending_gesture:
            self._pending_count += 1
        else:
            self._pending_gesture = raw.gesture
            self._pending_count = 1
        if self._pending_count >= self._dwell_windows:
            self._committed_gesture = raw.gesture
        return DecoderOutput(
            gesture=self._committed_gesture,
            confidence=raw.confidence,
            abstained=False,
        )
