> **WITHDRAWN HISTORICAL EVIDENCE.** This report predates the corrected evaluation and contains invalid or unsupported results. It must not support current scientific claims. See REPAIR_2026-10-01_REPORT.md and the regenerated results.

# M1: Preregistration report

Date: 2026-09-30. Status: **PASS**.

## Deliverables

- [docs/PREREGISTRATION.md](../PREREGISTRATION.md) frozen before any results were computed.
- SHA-256: `15a1f7dd67a45e8848baa8a88ce6f752b66b46984388064dc037c560b5c04f38` in [docs/PREREGISTRATION.sha256](../PREREGISTRATION.sha256).

## Design summary

Streaming 200 ms / 40 ms causal windows on GRABMyoFlow static trials. Four decoders, three shift axes, trial-level bootstrap uncertainty. Ground truth from trial gesture IDs only.

## Gate

Preregistration written and hashed before `scripts/run_benchmark.py` was first executed.
