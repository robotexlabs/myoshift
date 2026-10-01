> **WITHDRAWN AGGREGATE HISTORICAL NOTE.** Retained as observed evidence with unverified provenance. This aggregate note is not the active repair ledger. The separate numbered 2026-10-01 amendments document the current repair after results had been seen. Claims in the historical body are not adopted without independent evidence.

# Amendment 2026-09-30 (repair round)

Results had already been computed before this amendment. The frozen preregistration file and its SHA-256 in `docs/PREREGISTRATION.sha256` were not edited.

## Changes after results were seen

1. Electrode mapping now keys full window identity; labels and rest flags must match exactly.
2. False activations count held command events with measured rest exposure; absent rest returns unavailable.
3. Bootstrap aggregation recomputes ratios on pooled resampled windows/trials, not per-trial means.
4. Calibration/test windows purge overlapping raw sample ranges; decoders reset state per trial.
5. Person-shift evaluation holds out each pilot participant separately; bootstrap resamples participant clusters.
6. Selective decoder fits on source only and calibrates on an independent calibration set; session affine step removed.
7. Few-shot baseline is marked unavailable when calibration lacks two classes (pilot rest-only calibration).
8. Features use twelve wrist channels (W1-W12) with within-ring cyclic shift for electrode proxy evaluation.
9. `RESULTS.md` and milestone tables are generated from `results/results.json` with mismatch checks.
10. Freeze chronology remains unverified; this dated amendment records post-hoc protocol repairs.
11. Pyright strict diagnostics restored; CI builds and smoke-tests wheels on Python 3.11 and 3.12.
12. README quick start uses `scripts/download_pilot.sh`; documentation licence scope unified.
13. CLI validates positive window/stride; download script adds timeout, byte cap and checksum verification.

## Stop rules

The preregistered decoder novelty stop remains acknowledged: hysteresis and MyoShift overlap on false activations in the historical run, so decoder novelty claims stay withdrawn.
