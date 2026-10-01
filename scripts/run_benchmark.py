#!/usr/bin/env python3
"""Regenerate benchmark results (single entry point for RESULTS.md)."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from myoshift.eval.benchmark import run_full_benchmark  # noqa: E402
from myoshift.types import BudgetConfig, StreamConfig  # noqa: E402


def main() -> None:
    data_root = ROOT / "data" / "raw" / "grabmyo-flow" / "static_extension_WFDB"
    output_dir = ROOT / "results"
    if not data_root.exists():
        raise SystemExit(f"Data not found: {data_root}")
    run_full_benchmark(
        data_root,
        output_dir,
        StreamConfig(),
        BudgetConfig(),
    )
    with tempfile.TemporaryDirectory(prefix="myoshift-plot-cache-") as plot_cache:
        os.environ["MPLCONFIGDIR"] = plot_cache
        from generate_documents import generate
        from generate_figures import main as generate_figures

        generate_figures()
        generate()
        generate(check=True)
    print(f"Results written to {(output_dir / 'results.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
