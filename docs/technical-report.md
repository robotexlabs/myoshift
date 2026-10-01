# MyoShift: corrected static-trial sEMG pilot

Draft technical report.

Generated from `results/results.json`, SHA-256 `caa8e1cc23016896fd945890506faafbcbeb82b1af6ffa11f809b2df7d99c4f0`. Python 3.11.15; software versions: `{"myoshift": "0.1.1", "numpy": "2.4.6", "scikit-learn": "1.9.1", "wfdb": "4.3.1"}`.

Protocol hash: `15a1f7dd67a45e8848baa8a88ce6f752b66b46984388064dc037c560b5c04f38`. Pre-result freeze chronology is unverified. All repair amendments were made after results had been seen.

## Problem and related work

Reliable command scoring requires preserved trial labels, measured exposure and independent calibration. This repair evaluates a small static-trial pilot; it does not demonstrate physiological onset detection or a new best decoder. [EMGBench](https://arxiv.org/abs/2410.23625) and the [generic neuromotor interface study](https://doi.org/10.1038/s41586-025-09255-w) are related work; no unverified omission in either is claimed.

## Data and method

Real GRABMyoFlow pilot: 96 records, 11712 windows, 4 participants (44, 45, 46, 47), 36 features from named wrist channels. Person and electrode shifts use all participant hold-out folds; session shift holds out session 3. Calibration is the original prefix budget with raw-support overlap purged. Every independent record resets decoder state. Source LDA fitting uses source labels only; selective calibration uses independent target windows and the same confidence score at calibration and prediction. There is no affine session adaptation or conformal guarantee. The fixed bespoke hysteresis reference uses the same source training data. All source-informed methods have the same optional target-window budget; few-shot has only target calibration labels and no source data.

Command onsets require one decision interval with non-rest output, confidence at least 0.5 and no abstention. Holding a command counts once, until rest, abstention, low confidence, a changed command or record boundary. One eligible gesture record is one metadata-defined event; any correct command in its eligible test portion detects it. Exposure covers actual decision intervals after feature warm-up, clipped to raw record duration. No exposure and no accepted predictions give unavailable rate and risk, respectively. See the amendments for the complete rule.

Intervals resample whole participant clusters with paired methods. They are descriptive small-pilot intervals: participant hold-out folds share training data. They do not establish population safety, and zero-count intervals are not equivalence tests.

## Experiments

The frozen dated protocol remains byte-identical; pre-result chronology is unverified. The repair amendments describe all departures after observing results. The within-ring channel permutation is a proxy, not a measured physical displacement.

## Person shift

| Decoder | Trial-event recall [95% interval] | Window recall [95% interval] | False events/rest hour [95% interval] | Risk [95% interval] | Coverage [95% interval] | Test windows | Gesture events | Participants | p95 predict ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| static_lda | 0.819 [0.694, 0.944] | 0.512 [0.381, 0.751] | 912.626 [0.000, 2636.475] | 0.398 [0.192, 0.523] | 1.000 [1.000, 1.000] | 11492 | 72 | 4 | 0.145 |
| hysteresis | 0.750 [0.611, 0.917] | 0.473 [0.347, 0.696] | 608.417 [0.000, 1723.849] | 0.423 [0.233, 0.540] | 1.000 [1.000, 1.000] | 11492 | 72 | 4 | 0.154 |
| few_shot | unavailable: few_shot baseline unavailable: calibration lacks two classes | | | | | | | | |
| myoshift | 0.333 [0.153, 0.597] | 0.073 [0.031, 0.137] | 0.000 [0.000, 0.000] | 0.239 [0.008, 0.589] | 0.074 [0.043, 0.108] | 11492 | 72 | 4 | 0.152 |

Measured eligible rest exposure: 106.505859 seconds. 96 independent test records.

## Session shift

| Decoder | Trial-event recall [95% interval] | Window recall [95% interval] | False events/rest hour [95% interval] | Risk [95% interval] | Coverage [95% interval] | Test windows | Gesture events | Participants | p95 predict ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| static_lda | 0.958 [0.875, 1.000] | 0.724 [0.463, 0.944] | 0.000 [0.000, 0.000] | 0.210 [0.043, 0.403] | 1.000 [1.000, 1.000] | 3849 | 24 | 4 | 0.145 |
| hysteresis | 0.750 [0.456, 1.000] | 0.695 [0.431, 0.913] | 0.000 [0.000, 0.000] | 0.232 [0.067, 0.426] | 1.000 [1.000, 1.000] | 3849 | 24 | 4 | 0.161 |
| few_shot | unavailable: few_shot baseline unavailable: calibration lacks two classes | | | | | | | | |
| myoshift | 0.458 [0.250, 0.708] | 0.217 [0.084, 0.287] | 0.000 [0.000, 0.000] | 0.003 [0.000, 0.009] | 0.166 [0.064, 0.220] | 3849 | 24 | 4 | 0.138 |

Measured eligible rest exposure: 36.227051 seconds. 32 independent test records.

## Electrode shift

| Decoder | Trial-event recall [95% interval] | Window recall [95% interval] | False events/rest hour [95% interval] | Risk [95% interval] | Coverage [95% interval] | Test windows | Gesture events | Participants | p95 predict ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| static_lda | 0.472 [0.375, 0.528] | 0.227 [0.134, 0.314] | 878.825 [0.000, 2636.475] | 0.611 [0.524, 0.685] | 1.000 [1.000, 1.000] | 11492 | 72 | 4 | 0.152 |
| hysteresis | 0.444 [0.326, 0.528] | 0.201 [0.111, 0.282] | 676.019 [0.000, 2028.057] | 0.625 [0.549, 0.699] | 1.000 [1.000, 1.000] | 11492 | 72 | 4 | 0.152 |
| few_shot | unavailable: few_shot baseline unavailable: calibration lacks two classes | | | | | | | | |
| myoshift | 0.111 [0.069, 0.139] | 0.017 [0.005, 0.036] | 33.801 [0.000, 101.403] | 0.581 [0.052, 0.901] | 0.031 [0.011, 0.053] | 11492 | 72 | 4 | 0.144 |

Measured eligible rest exposure: 106.505859 seconds. 96 independent test records.

## Paired participant comparisons

| Shift | Contrast | Event recall difference [95% interval] | Window recall difference [95% interval] | Coverage difference [95% interval] |
|---|---|---|---|---|
| person | myoshift minus static_lda | -0.486 [-0.667, -0.306] | -0.439 [-0.610, -0.333] | -0.926 [-0.957, -0.892] |
| person | myoshift minus hysteresis | -0.417 [-0.569, -0.278] | -0.400 [-0.555, -0.304] | -0.926 [-0.957, -0.892] |
| session | myoshift minus static_lda | -0.500 [-0.667, -0.292] | -0.507 [-0.681, -0.216] | -0.834 [-0.936, -0.780] |
| session | myoshift minus hysteresis | -0.292 [-0.500, -0.083] | -0.477 [-0.645, -0.185] | -0.834 [-0.936, -0.780] |
| electrode | myoshift minus static_lda | -0.361 [-0.389, -0.306] | -0.210 [-0.289, -0.124] | -0.969 [-0.989, -0.947] |
| electrode | myoshift minus hysteresis | -0.333 [-0.389, -0.257] | -0.184 [-0.258, -0.101] | -0.969 [-0.989, -0.947] |

## Interpretation and limitations

Person-shift selective window recall is lower than static LDA: 0.073 [0.031, 0.137] versus 0.512 [0.381, 0.751]. Trial-event recall is a separate, coarse detection metric, not physiological event timing. The available runs counted 92 false command events in total across the repeated method evaluations. Short laboratory rest exposure and a zero-count bootstrap interval cannot establish safety equivalence. Decoder novelty remains withdrawn. Threshold-swept risk-coverage and matched-recall comparisons are untested. Person coverage stop rule fired: False. Hysteresis interval-overlap novelty stop fired: True. This withdrawal stop is not an equivalence test. The few-shot baseline is unavailable under the frozen rest-only calibration prefix. No general benchmark novelty or clinical usefulness is established by this repair.

GRABMyoFlow participants are healthy adults recorded in seated laboratory conditions; clinical or impaired-population generalisation is untested. Person and electrode shifts each fit one model per held-out participant with a 50-window calibration prefix on that participant's unpermuted windows (200 windows across four folds). Session shift pools all participants' held-out session-3 windows and takes one global 50-window prefix before thresholding all four participants together. That prefix is the first lexicographically ordered windows of participant 44's session-3 rest record, not a separate calibration per participant. Electrode shift calibrates on the held-out participant's unpermuted prefix, then permutes only test features within each wrist ring, combining participant hold-out with a synthetic post-calibration channel change. Feature samples for the full pilot are materialised before replay; waveforms load trial by trial. This is causal-window offline replay without validated live acquisition, continuous transitions or physiological onset timing. Trial-level detection saturates easily and cannot measure physiological timing. Calibration contains only rest and cannot validate gesture-conditioned confidence rejection. decoder.predict call only; excludes feature extraction, acquisition and end-to-end command response; The governing compressed/swapped footprint gate remains unverified when measurement is blocked or unavailable. No second dataset, external official controller, population safety claim or threshold frontier has been validated.

## Resources

Full evaluation runtime: 20.370 s. Cumulative process peak RSS: 240.312 MiB. Host: Mac-Studio.local; platform: macOS-27.0.1-arm64-arm-64bit. Footprint measurement: blocked or unavailable. Latency p95 columns time `decoder.predict` only; they exclude feature extraction, acquisition and end-to-end command response. RSS is not isolated evaluation memory or macOS compressed/swapped footprint. The required footprint gate remains unverified when measurement is blocked or unavailable.


## References

GRABMyoFlow: [Ehlert, Tung and Pradhan, PhysioNet 1.0.0](https://doi.org/10.13026/ah52-zq51), CC BY 4.0. The official extension converter selects wrist indices 1-6 and 9-14. PhysioNet platform (current): Pollard T, Moody BE, Lehman L, Gow B, Fernandes C, Xie C, Johnson A, Mark RG, Heldt T. PhysioNet as a global platform for biomedical research. Nature Health. 2026. doi:10.1038/s44360-026-00096-z. Earlier platform citation: Goldberger AL, Amaral LAN, Glass L, et al. Circulation. 2000;101(23):e215-e220.
