> **WITHDRAWN HISTORICAL EVIDENCE.** This report predates the corrected evaluation and contains invalid or unsupported results. It must not support current scientific claims. See REPAIR_2026-10-01_REPORT.md and the regenerated results.

# M0: Novelty and data gate report

Date: 2026-09-30. Status: **PASS** (proceed to M1).

## Research question (proposed contribution)

Does a **streaming, event-level benchmark** with a **budgeted selective decoder** improve the false-activation versus recall frontier under person, session and electrode shift, compared with standard offline accuracy metrics and generic large-scale sEMG decoders?

This is **not** another cross-person accuracy paper. The contribution is the evaluation contract (event-level safety metrics, calibration budget, abstention) and a lightweight decoder that targets that contract.

## Prior art checked (2026-09-30)

| Work | Relationship | Verified |
|------|--------------|----------|
| [EMGBench (NeurIPS 2024)](https://arxiv.org/abs/2410.23625) | OOD generalization benchmark across nine datasets; window-level accuracy, not streaming false activations | Sourced |
| [Meta generic neuromotor interface (Nature 2025)](https://doi.org/10.1038/s41586-025-09255-w) | Large generic decoder; CC BY-NC-SA data; no abstention or deployment budget | Sourced |
| [emg2pose (2024)](https://arxiv.org/abs/2412.02725) | Continuous pose from HD sEMG; different task | Sourced |
| [LibEMG](https://github.com/LibEMG/libemg) | Toolkit and pipelines; not an event-safety benchmark | Verified (repo exists) |
| Electrode-shift augmentation papers (2024-2025) | Mitigation methods exist; no unified streaming safety benchmark | Sourced |

**Novelty assessment:** EMGBench and Meta cover generalization and scale. Neither publishes a preregistered **event-level false-activation benchmark** with **fixed calibration budget**, **abstention risk-coverage**, and **latency** under **electrode-shift simulation** on licensable public wrist sEMG. The gap is defensible if results are measured honestly on real data.

## Dataset licence gate

| Dataset | Licence | Company use | Size (pilot) | Role |
|---------|---------|-------------|--------------|------|
| GRABMyoFlow 1.0.0 | **Verified** CC BY 4.0 ([LICENSE.txt](https://physionet.org/files/grabmyo-flow/1.0.0/LICENSE.txt)) | Permitted with attribution | 4.3 GB full; **30 MB** pilot (4 participants, 3 sessions, gestures 1-3 and 17) | Primary |
| NinaPro DB6 | **Unknown** (no explicit file licence on official page) | **Excluded** until clarified | ~10 subjects, 7 grasps | Secondary replication only |
| Meta neuromotor release | CC BY-NC-SA 4.0 | **Excluded** (non-commercial) | 263 h | Not used |
| Hyser PR subset | ODC-By 1.0 | Permitted | 37 GB gesture subset | Deferred (size) |

**Gate decision:** Build on **GRABMyoFlow** only for M2-M3. NinaPro and Meta excluded from mandatory evaluation.

## Deployment budget (frozen for preregistration)

| Parameter | Value | Rationale |
|-------------|-------|-----------|
| Streaming window | 200 ms | Causal control latency |
| Stride | 40 ms | 25 Hz update rate |
| Calibration budget | 50 windows (~2 s effective) | Wearable cold-start |
| Inference p95 target | 50 ms | Real-time UI |
| Peak RAM cap (process) | 8 GB (target 2 GB decoder path) | Mac Studio watchdog |
| Download cap | 20 GB | Pilot subset |

## Credible result (go/no-go, preregistered)

At matched gesture **event recall** on held-out participants:

1. **False activations per rest hour** reduced by at least **50%** versus the strongest **hysteresis** baseline, with subject-level bootstrap 95% CI excluding zero improvement.
2. Retain at least **90%** of baseline event recall.
3. MyoShift **risk-coverage** curve dominates static LDA on person shift (lower risk at equal or higher coverage).

**Kill test:** If MyoShift wins only by abstaining on nearly all windows, or hysteresis matches after tuning, report as negative result and stop claiming decoder novelty.

## Stop decision

M0 **passes**. Data exists, licence permits company research use, and the contribution is distinct from EMGBench accuracy framing and Meta generic decoding.
