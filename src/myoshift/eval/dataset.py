"""Build window samples from trial records (streaming, one trial at a time)."""

from __future__ import annotations

from pathlib import Path

from myoshift.data.grabmyo import (
    discover_trials,
    is_rest_gesture,
    iter_trial_windows,
    load_trial_emg,
)
from myoshift.features.extract import apply_channel_shift, extract_window_features
from myoshift.types import StreamConfig, WindowSample


def build_window_samples(
    data_root: Path,
    stream_config: StreamConfig,
    channel_shift: int = 0,
    max_trials: int | None = None,
) -> list[WindowSample]:
    trials = discover_trials(data_root)
    if max_trials is not None:
        trials = trials[:max_trials]
    samples: list[WindowSample] = []
    window_samples = stream_config.window_samples
    stride_samples = stream_config.stride_samples
    for trial in trials:
        emg = load_trial_emg(trial.emg_path)
        if channel_shift:
            emg = apply_channel_shift(emg, channel_shift)
        trial_key = (
            f"p{trial.participant_id}_s{trial.session_id}_g{trial.gesture_id}_t{trial.trial_id}"
        )
        for start_idx, window in iter_trial_windows(emg, window_samples, stride_samples):
            features = extract_window_features(window, stream_config.sample_rate_hz)
            time_s = start_idx / stream_config.sample_rate_hz
            samples.append(
                WindowSample(
                    features=features,
                    label=trial.gesture_id,
                    participant_id=trial.participant_id,
                    session_id=trial.session_id,
                    trial_key=trial_key,
                    time_s=time_s,
                    is_rest=is_rest_gesture(trial.gesture_id),
                    start_sample=start_idx,
                    end_sample=start_idx + window_samples,
                    decision_duration_s=min(
                        stride_samples, trial.n_samples - start_idx - window_samples
                    )
                    / stream_config.sample_rate_hz,
                )
            )
    return samples


def samples_to_arrays(
    samples: list[WindowSample],
) -> tuple[list[WindowSample], list[int]]:
    labels = [s.label for s in samples]
    return samples, labels
