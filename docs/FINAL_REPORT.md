> **WITHDRAWN HISTORICAL EVIDENCE.** This report predates the corrected evaluation and contains invalid or unsupported results. It must not support current scientific claims. See REPAIR_2026-10-01_REPORT.md and the regenerated results.

# MyoShift final report

Date: 2026-09-30.

## What was built

MyoShift is an open-source Python package providing:

1. A **streaming event-level evaluation protocol** for surface EMG gesture decoding under person, session and electrode shift.
2. A **budgeted selective decoder** (session normalization + LDA + conformal-style abstention).
3. Reproducible benchmark scripts, results JSON, figures, preregistration, and documentation.

## Milestone outcomes

| Milestone | Result |
|-----------|--------|
| M0 | PASS: GRABMyoFlow CC BY 4.0; novelty gap vs EMGBench/Meta framing confirmed |
| M1 | PASS: preregistration frozen (SHA-256 recorded) |
| M2 | PASS: typed implementation on real WFDB data |
| M3 | PASS: evaluation complete; **decoder hypotheses not supported** on pilot |

## Measured results (person shift)

- static LDA recall: **0.306** [0.161, 0.484]
- MyoShift recall: **0.183** [0.055, 0.344], coverage **0.304**
- False activations: **0.0** / rest hour for all decoders (saturated metric on pilot)
- Full benchmark runtime: **~138 s**; peak RSS **~224 MB**

## Tests and quality

| Check | Status |
|-------|--------|
| pytest | 32 passed |
| Coverage (library) | **92.2%** |
| ruff | clean |
| mypy | clean |
| pyright | clean |

## What is missing

- Larger participant and gesture coverage (full GRABMyoFlow or second dataset with clear licence).
- NinaPro DB6 replication (licence not verified for company use).
- Continuous free-living rest segments (pilot rest trials are short laboratory holds).
- Independent human review of event labels (labels are trial metadata, not hand-annotated onset times).
- Latency relative to physiological onset (only classifier call time measured).

## Deviations

- `few_shot` baseline falls back to full training data when calibration windows contain fewer than two classes (preregistered budget can sit inside one gesture trial).
- Electrode shift uses cyclic channel permutation (+2), a proxy for displacement rather than measured shift.
- Peak memory reported from `resource.getrusage` in-process; `top` was unavailable in the execution environment.
