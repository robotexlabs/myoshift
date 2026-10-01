"""Command-line interface for MyoShift."""

from __future__ import annotations

from pathlib import Path

import click
import numpy as np

from myoshift.eval.benchmark import run_full_benchmark
from myoshift.types import BudgetConfig, StreamConfig


@click.group()
@click.version_option(package_name="myoshift")
def main() -> None:
    """MyoShift streaming sEMG benchmark and selective decoder."""


@main.command("benchmark")
@click.option(
    "--data-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Path to GRABMyoFlow static_extension_WFDB parent directory",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("results"),
    help="Directory for results.json and prediction traces",
)
@click.option("--calibration-windows", type=click.IntRange(min=0), default=50)
@click.option("--window-ms", type=click.IntRange(min=1), default=200)
@click.option("--stride-ms", type=click.IntRange(min=1), default=40)
def benchmark_cmd(
    data_root: Path,
    output_dir: Path,
    calibration_windows: int,
    window_ms: int,
    stride_ms: int,
) -> None:
    """Run the preregistered benchmark on local GRABMyoFlow data."""
    stream = StreamConfig(window_ms=window_ms, stride_ms=stride_ms)
    budget = BudgetConfig(max_calibration_windows=calibration_windows)
    results = run_full_benchmark(data_root, output_dir, stream, budget)
    click.echo(f"Wrote {output_dir / 'results.json'} ({len(results['runs'])} runs)")


@main.command("verify-scorers")
def verify_scorers_cmd() -> None:
    """Verify perfect and empty scorer behaviour through production bootstrap."""
    from myoshift.eval.metrics import (
        bootstrap_by_trial,
        empty_score,
        perfect_score,
        score_windows,
    )
    from myoshift.models.base import DecoderOutput
    from myoshift.types import REST_GESTURE_ID, WindowSample

    gesture = WindowSample(
        features=np.zeros(3),
        label=1,
        participant_id=1,
        session_id=1,
        trial_key="t1",
        time_s=0.0,
        is_rest=False,
        decision_duration_s=0.04,
    )
    rest = WindowSample(
        features=np.zeros(3),
        label=REST_GESTURE_ID,
        participant_id=1,
        session_id=1,
        trial_key="t2",
        time_s=0.0,
        is_rest=True,
        decision_duration_s=0.04,
    )
    perfect_outputs = [
        DecoderOutput(gesture=1, confidence=0.9, abstained=False),
        DecoderOutput(gesture=REST_GESTURE_ID, confidence=0.9, abstained=False),
    ]
    empty_outputs = [DecoderOutput(gesture=2, confidence=0.9, abstained=True)] * 2
    perfect = {
        key: value.value
        for key, value in bootstrap_by_trial(
            score_windows([gesture, rest], perfect_outputs),
            n_resamples=50,
        ).items()
    }
    empty = {
        key: value.value
        for key, value in bootstrap_by_trial(
            score_windows([gesture, rest], empty_outputs),
            n_resamples=50,
        ).items()
    }
    for actual, expected in [(perfect, perfect_score()), (empty, empty_score())]:
        for key, value in expected.items():
            if actual[key] != value:
                raise click.ClickException(f"Scorer failed on {key}: {actual[key]} != {value}")
    click.echo("Scorer verification passed")


if __name__ == "__main__":
    main()
