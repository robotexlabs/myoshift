"""LDA baseline decoder."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from myoshift._external import discriminant, preprocessing
from myoshift.models.base import Decoder, DecoderOutput
from myoshift.types import REST_GESTURE_ID


class LdaDecoder(Decoder):
    def __init__(self, rest_gesture_id: int = REST_GESTURE_ID) -> None:
        self._rest_gesture_id = rest_gesture_id
        self._scaler = preprocessing.StandardScaler()
        self._lda = discriminant.LinearDiscriminantAnalysis()
        self._classes: NDArray[np.int_] | None = None

    def fit(self, x: NDArray[np.floating], y: NDArray[np.int_]) -> None:
        x_scaled = self._scaler.fit_transform(x)
        self._lda.fit(x_scaled, y)
        self._classes = np.asarray(self._lda.classes_, dtype=np.int_)

    def predict(self, x: NDArray[np.floating]) -> DecoderOutput:
        if self._classes is None:
            raise RuntimeError("Decoder not fitted")
        x_scaled = self._scaler.transform(x.reshape(1, -1))
        proba = self._lda.predict_proba(x_scaled)[0]
        idx = int(np.argmax(proba))
        gesture = int(self._classes[idx])
        confidence = float(proba[idx])
        return DecoderOutput(gesture=gesture, confidence=confidence, abstained=False)
