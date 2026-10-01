# MyoShift preregistration

Frozen: 2026-09-30. Do not edit after results are computed. Amendments go in `docs/AMENDMENT_*.md`.

## Question

Under person, session and electrode shift, does a budgeted selective streaming decoder reduce false gesture activations while preserving event recall, compared with static LDA, few-shot calibration and hysteresis baselines?

## Data

- **Primary:** GRABMyoFlow 1.0.0 static extension (PhysioNet), CC BY 4.0.
- **Pilot subset:** participants 44-47, sessions 1-3, gestures 1, 2, 3 and 17 (rest), trials 1-2.
- **Excluded:** NinaPro (licence unknown), Meta neuromotor data (CC BY-NC-SA).

Ground-truth labels come from trial metadata (gesture ID per WFDB record). They are **not** derived from classifier outputs.

## Streaming protocol

- Sample rate: 2048 Hz (dataset native).
- Causal window: 200 ms; stride 40 ms.
- Features per window: per-channel MAV, RMS, 20-450 Hz bandpower (36 features for 12 active wrist channels in pilot files).
- Trials processed sequentially; windows within a trial labelled by trial gesture ID.

## Shift evaluations

| Shift | Train | Calibration | Test | Held out |
|-------|-------|-------------|------|----------|
| Person | All windows from participants not in test set | First 50 test-participant windows | Remaining test-participant windows | Participant 47 |
| Session | Sessions 1-(T-1) all participants | First 50 session-T windows | Remaining session-T windows | Session 3 |
| Electrode | Unshifted channels | First 50 test windows (unshifted calib) | Cyclic channel shift +2 on test stream | Shift magnitude 2 |

## Decoders (baselines and proposed)

| Name | Description |
|------|-------------|
| `static_lda` | LDA on source subjects, no adaptation |
| `few_shot` | LDA fit on calibration budget only |
| `hysteresis` | LDA + confidence threshold 0.55 + dwell 3 windows |
| `myoshift` | Session z-score from calibration + LDA + conformal abstention (90% calibration coverage target, margin 0.15) |

No hyperparameter search on test data. Thresholds fixed before evaluation.

## Metrics

Primary:

- **False activations per rest hour** (non-rest prediction with confidence >= 0.5 during rest trials).
- **Event recall** (correct non-abstained gesture windows / all gesture windows).

Secondary:

- Risk-coverage (error rate on non-abstained windows vs coverage).
- Latency p50/p95 per predict call (proxy; not physiological onset).
- Peak RSS MB, total runtime.

Uncertainty: bootstrap by **trial** (500 resamples, 95% CI).

## Success criteria

See M0_REPORT.md credible-result contract.

## Stop rules

1. If MyoShift coverage < 5% on person shift, stop and report abstention failure.
2. If hysteresis matches MyoShift false-activation rate within CI on all shifts, stop decoder novelty claims.
3. If peak process memory exceeds 12 GB on pilot, reduce subset and document.

## Reproduction command

```bash
pip install -e ".[dev]"
python scripts/run_benchmark.py
python scripts/generate_figures.py
```

Results written to `results/results.json` and `results/figures/`.
