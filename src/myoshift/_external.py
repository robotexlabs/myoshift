"""Typed contracts at the WFDB and scikit-learn dependency boundaries."""

from __future__ import annotations

from importlib import import_module
from typing import Protocol, cast

from myoshift.types import FloatArray, IntArray


class Header(Protocol):
    n_sig: int
    sig_len: int
    fs: float
    sig_name: list[str]
    p_signal: FloatArray | None


class WfdbAPI(Protocol):
    def rdheader(self, record_name: str) -> Header: ...
    def rdrecord(self, record_name: str, *, physical: bool = True) -> Header: ...


class Scaler(Protocol):
    def fit_transform(self, x: FloatArray) -> FloatArray: ...
    def transform(self, x: FloatArray) -> FloatArray: ...


class Lda(Protocol):
    classes_: IntArray

    def fit(self, x: FloatArray, y: IntArray) -> object: ...
    def predict_proba(self, x: FloatArray) -> FloatArray: ...


class Preprocessing(Protocol):
    def StandardScaler(self) -> Scaler: ...


class Discriminant(Protocol):
    def LinearDiscriminantAnalysis(self) -> Lda: ...


wfdb = cast(WfdbAPI, import_module("wfdb"))
preprocessing = cast(Preprocessing, import_module("sklearn.preprocessing"))
discriminant = cast(Discriminant, import_module("sklearn.discriminant_analysis"))
