#!/usr/bin/env python3
"""Compatibility entry point for the complete foreground reproduction command."""

from pathlib import Path
from runpy import run_path

if __name__ == "__main__":
    run_path(str(Path(__file__).with_name("run_benchmark.py")), run_name="__main__")
