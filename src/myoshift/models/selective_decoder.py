"""Source-fitted LDA with an independent empirical confidence calibration."""

from __future__ import annotations

import numpy as np

from myoshift.models.base import DecoderOutput
from myoshift.models.lda_baseline import LdaDecoder
from myoshift.types import REST_GESTURE_ID, FloatArray, IntArray


class SelectiveDecoder(LdaDecoder):
    """Empirical confidence rejection; no conformal or adaptation guarantee."""

    def __init__(
        self,
        rest_gesture_id: int = REST_GESTURE_ID,
        coverage_target: float = 0.90,
        margin_min: float = 0.15,
    ) -> None:
        super().__init__(rest_gesture_id)
        self._coverage_target = coverage_target
        self._margin_min = margin_min
        self._abstain_threshold: float | None = None
        self.n_calibration = 0

    @property
    def score_threshold(self) -> float | None:
        return self._abstain_threshold

    def fit(self, x: FloatArray, y: IntArray) -> None:
        super().fit(x, y)
        self._abstain_threshold = None
        self.n_calibration = 0

    def calibrate(self, x: FloatArray) -> None:
        if self._classes is None:
            raise RuntimeError("Decoder not fitted")
        if not len(x):
            raise ValueError("selective calibration unavailable: no independent windows")
        probabilities = self._lda.predict_proba(self._scaler.transform(x))
        scores = 1.0 - np.max(probabilities, axis=1)
        self._abstain_threshold = float(np.quantile(scores, self._coverage_target))
        self.n_calibration = len(x)

    def predict(self, x: FloatArray) -> DecoderOutput:
        if self._classes is None:
            raise RuntimeError("Decoder not fitted")
        if self._abstain_threshold is None:
            raise RuntimeError("Decoder not independently calibrated")
        probabilities = self._lda.predict_proba(self._scaler.transform(x.reshape(1, -1)))[0]
        order = np.argsort(probabilities)[::-1]
        top = int(order[0])
        second = int(order[1]) if len(order) > 1 else top
        confidence = float(probabilities[top])
        gesture = int(self._classes[top])
        abstained = (
            1.0 - confidence > self._abstain_threshold
            or float(probabilities[top] - probabilities[second]) < self._margin_min
            or gesture == self._rest_gesture_id
        )
        return DecoderOutput(gesture, confidence, abstained)
