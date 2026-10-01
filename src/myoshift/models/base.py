"""Decoder base protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class DecoderOutput:
    gesture: int
    confidence: float
    abstained: bool


class Decoder(ABC):
    @abstractmethod
    def fit(self, x: NDArray[np.floating], y: NDArray[np.int_]) -> None: ...

    @abstractmethod
    def predict(self, x: NDArray[np.floating]) -> DecoderOutput: ...

    def reset_state(self) -> None:
        """Reset state before an independent record (stateless default)."""
        return None

    def predict_batch(self, x: NDArray[np.floating]) -> list[DecoderOutput]:
        return [self.predict(row) for row in x]
