> **WITHDRAWN HISTORICAL EVIDENCE.** This report predates the corrected evaluation and contains invalid or unsupported results. It must not support current scientific claims. See REPAIR_2026-10-01_REPORT.md and the regenerated results.

# M2: Implementation report

Date: 2026-09-30. Status: **PASS**.

## Built

- Typed `src/myoshift` package: WFDB streaming loader, feature extraction, four decoders, split policies, metrics, CLI.
- Pilot data: 96 GRABMyoFlow WFDB records (~30 MB) under `data/raw/`.
- Reproduction entry points: `scripts/run_benchmark.py`, `myoshift benchmark`, `myoshift verify-scorers`.

## Memory

Peak RSS per evaluation run measured at **~224 MB** (well under 8 GB cap). Data loaded one trial at a time; no full-dataset tensors held in memory.

## Gate

Core method runs on real public WFDB recordings with documented licences.
