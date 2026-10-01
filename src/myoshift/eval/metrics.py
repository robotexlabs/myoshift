"""Command-event scoring and ratio bootstrap over complete clusters."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import numpy as np

from myoshift.models.base import DecoderOutput
from myoshift.types import REST_GESTURE_ID, FloatArray, MetricResult, WindowSample

NAMES = ("false_activations_per_rest_hour", "event_recall", "window_recall", "risk", "coverage")


@dataclass(frozen=True)
class ScoredWindow:
    true_label: int
    output: DecoderOutput
    is_rest: bool
    time_s: float
    trial_key: str
    participant_id: int = 0
    session_id: int = 0
    decision_duration_s: float | None = None
    start_sample: int | None = None
    end_sample: int | None = None

    @property
    def identity(self) -> tuple[int, int, str, float, int | None, int | None]:
        return (
            self.participant_id,
            self.session_id,
            self.trial_key,
            self.time_s,
            self.start_sample,
            self.end_sample,
        )


def sufficient_statistics(scored: list[ScoredWindow]) -> FloatArray:
    """False onsets, rest seconds, detected/eligible events, correct/eligible windows,
    errors/accepted windows, all windows. Summing preserves metric eligibility.
    """
    stats = np.zeros(9, dtype=np.float64)
    records: dict[tuple[int, int, str], list[ScoredWindow]] = defaultdict(list)
    for s in scored:
        records[(s.participant_id, s.session_id, s.trial_key)].append(s)
        stats[8] += 1
        if not s.output.abstained:
            stats[7] += 1
            stats[6] += s.output.gesture != s.true_label
        if not s.is_rest:
            stats[5] += 1
            stats[4] += not s.output.abstained and s.output.gesture == s.true_label
    for windows in records.values():
        windows.sort(key=lambda s: s.time_s)
        gaps = np.diff([s.time_s for s in windows])
        inferred = float(np.median(gaps)) if len(gaps) else None
        previous: int | None = None
        detected = False
        eligible = any(not s.is_rest for s in windows)
        for s in windows:
            duration = s.decision_duration_s if s.decision_duration_s is not None else inferred
            if s.is_rest and duration is not None:
                stats[1] += duration
            command = (
                s.output.gesture
                if not s.output.abstained
                and s.output.confidence >= 0.5
                and s.output.gesture != REST_GESTURE_ID
                else None
            )
            if s.is_rest and command is not None and command != previous:
                stats[0] += 1
            if not s.is_rest and command == s.true_label:
                detected = True
            previous = command
        stats[3] += eligible
        stats[2] += eligible and detected
    return stats


def scores_from_statistics(stats: FloatArray) -> dict[str, float | None]:
    def ratio(numerator: int, denominator: int, scale: float = 1) -> float | None:
        return float(stats[numerator] / stats[denominator] * scale) if stats[denominator] else None

    return {
        NAMES[0]: ratio(0, 1, 3600),
        NAMES[1]: ratio(2, 3),
        NAMES[2]: ratio(4, 5),
        NAMES[3]: ratio(6, 7),
        NAMES[4]: ratio(7, 8),
    }


def compute_scores(scored: list[ScoredWindow]) -> dict[str, float | None]:
    return scores_from_statistics(sufficient_statistics(scored))


def false_activations_per_rest_hour(scored: list[ScoredWindow]) -> float | None:
    return compute_scores(scored)[NAMES[0]]


def event_recall(scored: list[ScoredWindow]) -> float | None:
    return compute_scores(scored)[NAMES[1]]


def risk_coverage(scored: list[ScoredWindow]) -> tuple[float | None, float | None]:
    scores = compute_scores(scored)
    return scores["risk"], scores["coverage"]


def perfect_score() -> dict[str, float | None]:
    return dict(zip(NAMES, [0.0, 1.0, 1.0, 0.0, 1.0], strict=True))


def empty_score() -> dict[str, float | None]:
    return dict(zip(NAMES, [0.0, 0.0, 0.0, None, 0.0], strict=True))


def bootstrap_ci(
    values: list[float],
    n_resamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> tuple[float, float, float]:
    if not values:
        return 0.0, 0.0, 0.0
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=np.float64)
    means = np.mean(rng.choice(arr, size=(n_resamples, len(arr))), axis=1)
    return (
        float(np.mean(arr)),
        float(np.quantile(means, alpha / 2)),
        float(np.quantile(means, 1 - alpha / 2)),
    )


def _group_statistics(scored: list[ScoredWindow], participant: bool) -> FloatArray:
    groups: dict[str, list[ScoredWindow]] = defaultdict(list)
    for s in scored:
        key = str(s.participant_id) if participant else str(s.identity[:3])
        groups[key].append(s)
    return np.asarray([sufficient_statistics(groups[k]) for k in sorted(groups)], dtype=np.float64)


def _metric_results(
    point: dict[str, float | None],
    draws: list[dict[str, float | None]],
) -> dict[str, MetricResult]:
    results: dict[str, MetricResult] = {}
    for name in NAMES:
        values = [draw[name] for draw in draws if draw[name] is not None]
        array = np.asarray(values, dtype=np.float64)
        low = float(np.quantile(array, 0.025)) if len(array) else None
        high = float(np.quantile(array, 0.975)) if len(array) else None
        results[name] = MetricResult(
            name, point[name], low, high, "events/hour" if name == NAMES[0] else "proportion"
        )
    return results


def _bootstrap(
    scored: list[ScoredWindow],
    participant: bool,
    n_resamples: int,
    seed: int,
) -> dict[str, MetricResult]:
    groups = _group_statistics(scored, participant)
    rng = np.random.default_rng(seed)
    draws: list[dict[str, float | None]] = []
    if len(groups):
        for _ in range(n_resamples):
            indices = rng.integers(0, len(groups), len(groups))
            draws.append(scores_from_statistics(np.sum(groups[indices], axis=0)))
    return _metric_results(compute_scores(scored), draws)


def bootstrap_by_trial(
    scored: list[ScoredWindow],
    n_resamples: int = 500,
    seed: int = 42,
) -> dict[str, MetricResult]:
    """Recompute ratios on whole resampled trials, never means of trial ratios."""
    return _bootstrap(scored, False, n_resamples, seed)


def bootstrap_by_participant(
    scored: list[ScoredWindow],
    n_resamples: int = 500,
    seed: int = 42,
) -> dict[str, MetricResult]:
    """Resample participants with all records, exposures and predictions attached."""
    return _bootstrap(scored, True, n_resamples, seed)


def paired_comparison(
    a: list[ScoredWindow],
    b: list[ScoredWindow],
    n_resamples: int = 500,
    seed: int = 42,
) -> dict[str, MetricResult]:
    """a minus b, using identical participant draws and exact test identities."""
    if [(s.identity, s.true_label, s.is_rest) for s in a] != [
        (s.identity, s.true_label, s.is_rest) for s in b
    ]:
        raise ValueError("paired comparison requires identical labelled test windows")
    ga, gb = _group_statistics(a, True), _group_statistics(b, True)

    def difference(sa: FloatArray, sb: FloatArray) -> dict[str, float | None]:
        va, vb = scores_from_statistics(sa), scores_from_statistics(sb)
        result: dict[str, float | None] = {}
        for name in NAMES:
            av, bv = va[name], vb[name]
            result[name] = av - bv if av is not None and bv is not None else None
        return result

    point = difference(sufficient_statistics(a), sufficient_statistics(b))
    rng = np.random.default_rng(seed)
    draws: list[dict[str, float | None]] = []
    if len(ga):
        for _ in range(n_resamples):
            indices = rng.integers(0, len(ga), len(ga))
            draws.append(difference(np.sum(ga[indices], axis=0), np.sum(gb[indices], axis=0)))
    return _metric_results(point, draws)


def score_windows(samples: list[WindowSample], outputs: list[DecoderOutput]) -> list[ScoredWindow]:
    if len(samples) != len(outputs):
        raise ValueError("samples and outputs length mismatch")
    identities = [
        (s.participant_id, s.session_id, s.trial_key, s.time_s, s.start_sample, s.end_sample)
        for s in samples
    ]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate window identity")
    return [
        ScoredWindow(
            s.label,
            o,
            s.is_rest,
            s.time_s,
            s.trial_key,
            s.participant_id,
            s.session_id,
            s.decision_duration_s,
            s.start_sample,
            s.end_sample,
        )
        for s, o in zip(samples, outputs, strict=True)
    ]
