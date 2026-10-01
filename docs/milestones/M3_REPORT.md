> **WITHDRAWN HISTORICAL EVIDENCE.** This report predates the corrected evaluation and contains invalid or unsupported results. It must not support current scientific claims. See REPAIR_2026-10-01_REPORT.md and the regenerated results.

# M3: Evaluation report

Date: 2026-09-30. Status: **PASS** (benchmark complete; decoder success criteria **not met**).

## Results source

All metrics from `results/results.json`, produced by `python scripts/run_benchmark.py`.

## Findings

1. **False activations:** 0.0 per rest hour for all decoders on this pilot (metric saturated; rest trials are short and classifiers rarely emit confident non-rest labels during rest).
2. **Person shift:** static LDA event recall 0.306 [0.161, 0.484]; MyoShift 0.183 [0.055, 0.344] at coverage 0.304.
3. **Session shift:** MyoShift lowers risk modestly at lower coverage versus static LDA; intervals overlap substantially.
4. **Electrode shift:** large degradation for all methods; MyoShift coverage 0.095.

## Stop rules (from preregistration)

- **Rule 2 fired:** hysteresis matches MyoShift on false activations (both zero). Decoder novelty claim **withdrawn**.
- **Success criteria not met:** no 50% false-activation reduction; MyoShift does not retain 90% of baseline recall on person shift.

## Baselines

| Decoder | Implementation |
|---------|------------------|
| static_lda | scikit-learn `LinearDiscriminantAnalysis` + `StandardScaler` |
| few_shot | LDA fit on calibration windows (falls back to train if <2 classes in calib) |
| hysteresis | LDA + threshold 0.55 + dwell 3 windows (preregistered) |
| myoshift | Session z-score + LDA + calibration quantile abstention |

## Uncertainty

Trial-level bootstrap, 500 resamples, 95% CI.

## Gate

Evaluation against preregistered baselines with uncertainty is complete. Negative decoder result reported honestly.
