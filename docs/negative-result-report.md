# No recall advantage for selective sEMG decoding in the corrected MyoShift pilot

## Abstract

Does a budgeted selective streaming decoder reduce false gesture commands while preserving recall under distribution shift? This corrected evaluation uses the GRABMyoFlow static-extension pilot, licensed under CC BY 4.0, with 4 participants, 96 records, 11712 extracted windows and 72 metadata-defined gesture events. Compared with static linear discriminant analysis (LDA), the selective decoder has no recall advantage under person, session or proxy electrode shift. Paired participant-bootstrap differences in trial-event recall, selective minus static LDA, are person: -0.486 [-0.667, -0.306]; session: -0.500 [-0.667, -0.292]; electrode: -0.361 [-0.389, -0.306]. Window recall is also lower under every shift. Reduced command emission accompanies substantial abstention, so these operating points do not establish a better risk-coverage trade-off or safety equivalence. The decoder novelty claim was withdrawn. This report replaces scientific interpretation of the earlier invalid evaluation with an auditable negative result, while retaining the frozen protocol, retrospective amendments and withdrawn outputs as evidence of the actual chronology.

## Background

Surface electromyography provides information about intended movement, but a classifier's behaviour can change across users, sessions and recording arrangements.

Prior work includes [EMGBench](https://arxiv.org/abs/2410.23625), which addresses out-of-distribution sEMG generalisation and adaptation, and the [generic non-invasive neuromotor interface study](https://doi.org/10.1038/s41586-025-09255-w). Neither work is re-evaluated here; no missing capability or unoccupied research area is claimed. The [GRABMyoFlow dataset extension](https://doi.org/10.13026/ah52-zq51), by Ehlert, Tung and Pradhan, supplies the public recordings. Only selected static records are evaluated. DOI metadata matches the repository references. These citations provide context, not decoder validation.

## Registered question and chronology

The [frozen protocol](PREREGISTRATION.md) asks whether budgeted selective streaming decoding reduces false activations while preserving event recall against static LDA, calibration-only few-shot LDA and hysteresis, under person, session and electrode shift. Its recorded hash is `15a1f7dd67a45e8848baa8a88ce6f752b66b46984388064dc037c560b5c04f38`. The hash matches the preserved protocol bytes. It establishes byte consistency; it does not independently establish that freezing occurred before results were inspected. The available provenance explicitly leaves pre-result freeze chronology unverified. Prospective registration is not established.

Amendments were made after seeing results. Dates are repair-round labels, not immutable timestamps. Finding identifiers are extracted from the linked records.

- 2026-09-30: [Withdrawn aggregate note](amendments/AMENDMENT_2026-09-30.md). Withdrawn aggregate historical repair note; superseded by the separate repair ledger.
- 2026-10-01; verification finding(s) 1: [Repair amendment 01: identity mapping](amendments/AMENDMENT_2026-10-01_01_identity_mapping.md). Require complete window identity and unchanged labels in shifted-data mapping.
- 2026-10-01; verification finding(s) 2: [Repair amendment 02: command events exposure](amendments/AMENDMENT_2026-10-01_02_command_events_exposure.md). Count command onsets and measured rest exposure; distinguish trial and window recall.
- 2026-10-01; verification finding(s) 3: [Repair amendment 03: ratio aggregation](amendments/AMENDMENT_2026-10-01_03_ratio_aggregation.md). Pool sufficient statistics before ratios; preserve undefined estimates as unavailable.
- 2026-10-01; verification finding(s) 4: [Repair amendment 04: purge and reset](amendments/AMENDMENT_2026-10-01_04_purge_and_reset.md). Purge overlapping raw support and reset decoder state at record boundaries.
- 2026-10-01; verification finding(s) 5: [Repair amendment 05: participant uncertainty](amendments/AMENDMENT_2026-10-01_05_participant_uncertainty.md). Use all participant hold-outs and paired participant uncertainty; frontier untested.
- 2026-10-01; verification finding(s) 6: [Repair amendment 06: independent selective calibration](amendments/AMENDMENT_2026-10-01_06_independent_selective_calibration.md). Use independent empirical calibration; remove cancelled normalisation and guarantees.
- 2026-10-01; verification finding(s) 7: [Repair amendment 07: unavailable few shot equal budget](amendments/AMENDMENT_2026-10-01_07_unavailable_few_shot_equal_budget.md). Remove few-shot fallback and state source-information budgets explicitly.
- 2026-10-01; verification finding(s) 8: [Repair amendment 08: verified wrist ring channels](amendments/AMENDMENT_2026-10-01_08_verified_wrist_ring_channels.md). Select named wrist channels and permute within each ring as a displacement proxy.
- 2026-10-01; verification finding(s) 9: [Repair amendment 09: generated reporting](amendments/AMENDMENT_2026-10-01_09_generated_reporting.md). Generate current reporting from results with mismatch checks and provenance.
- 2026-10-01; verification finding(s) 11: [Repair amendment 10: strict engineering](amendments/AMENDMENT_2026-10-01_10_strict_engineering.md). Restore strict typing diagnostics and isolated wheel verification.
- 2026-10-01; verification finding(s) 13: [Repair amendment 11: integer validation](amendments/AMENDMENT_2026-10-01_11_integer_validation.md). Validate dimensions and budgets; keep resource-measurement limitations explicit.
- 2026-10-01; verification finding(s) 5, 9: [Repair amendment 12: retained novelty withdrawal stop](amendments/AMENDMENT_2026-10-01_12_retained_novelty_stop.md). Retain the conservative novelty withdrawal stop; overlap is not safety equivalence.
- 2026-10-01: [Retrospective resource amendment, 2026-10-01](amendments/AMENDMENT_2026-10-01_13_resource_cap.md). Reconcile the stricter resource cap; footprint compliance remains unverified.
- 2026-10-01: [Retrospective protocol serialization amendment, 2026-10-01](amendments/AMENDMENT_2026-10-01_14_protocol_serialization.md). Pin CRLF protocol bytes in Git and record the LF checkout correction.

The [withdrawn historical outputs](../results/historical_2026-09-30/WITHDRAWN.md) must not support scientific claims. The earlier evaluation had invalid shifted-window mapping, corrupted electrode-condition labels, incorrect command-event counting and exposure, and inappropriate ratio aggregation. It also allowed overlapping calibration and test support, carried state across independent records, used insufficient uncertainty units, misrepresented selective calibration and substituted a static classifier when calibration-only fitting was impossible.

The earlier reported recall and corrected trial-event recall are different estimands. Changed hold-outs and repaired labels also preclude a direct before-and-after comparison. Old files support auditing, not scientific interpretation. Corrections were made after observing outcomes, so this report is a retrospective corrected analysis of the registered question. Engineering checks do not restore the original chronology.

## Methods

The pilot has 4 healthy adult participants recorded in seated laboratory conditions and 96 independent static records. Clinical or impaired-population generalisation is untested. Feature extraction produces 11712 windows at a native sampling rate of 2048 Hz, using nominal causal windows of 200 ms and strides of 40 ms. Named wrist channels produce 36 features using mean absolute value, root mean square and bandpower. Exposure uses actual integer sample support. Ground truth is the gesture identity supplied by trial metadata, independent of predictions from every decoder.

Person shift uses participant hold-out folds, training on the remaining participants. Session shift trains on earlier sessions and holds out the final selected session. Electrode shift uses held-out participant evaluation with a separate cyclic permutation inside each wrist ring. Mapping preserves full window identity, raw sample support, gesture labels and rest flags. This permutation approximates a change in channel arrangement. It does not reproduce a measured physical displacement, changing contact impedance or all consequences of reapplying electrodes.

The calibration prefix is limited to 50 target windows. Test windows sharing raw support with calibration are purged, and decoder state resets at independent record boundaries. Record order does not imply continuous acquisition. The source-informed methods share the same labelled source support and optional target calibration budget. Static LDA and the bespoke hysteresis reference do not consume that optional budget. Hysteresis applies fixed confidence and dwell rules to source LDA; it is a bespoke reference, not a verified strongest controller.

The selective decoder fits LDA and scaling on source data only. An independent target prefix sets an empirical confidence-rejection threshold using the same score applied at prediction. Fixed margin rejection and rest abstention remain. The removed session normalisation cancelled within refitting and cannot support an adaptation claim. Empirical calibration supplies no conformal guarantee. The prefix contains rest alone, so it cannot establish gesture-conditioned calibration performance.

Calibration-only few-shot LDA has no source data and requires multiple calibration classes. Under the preserved prefix it cannot fit. It is recorded as unavailable, including its reason, throughout the results. No fallback score or comparison with a successfully fitted few-shot system is available. Adding gesture examples would require a separately declared evaluation.

A command onset is an eligible non-rest, sufficiently confident, non-abstained decision, or a change to another command. Holding the same command counts once until offset. Trial-event recall counts a metadata-defined gesture record as detected if a correct command occurs in its eligible test portion. Window recall instead counts correct accepted gesture windows over eligible gesture windows. Trial detection can remain high despite inconsistent windows. False commands are normalised by measured eligible rest exposure. Risk is error among accepted windows; coverage is the accepted fraction. Undefined exposure or accepted support produces an unavailable estimate rather than a fabricated rate.

Uncertainty resamples complete participant clusters and keeps paired methods together. Sufficient statistics are pooled before each ratio is formed. Differences preserve method pairing. The displayed intervals are descriptive participant-bootstrap intervals conditional on this pilot, with shared training data across hold-out folds. They are not independent-population safety guarantees. Repeated records do not add independent participants.

## Results

All tables below are generated from `results/results.json`, whose digest is `caa8e1cc23016896fd945890506faafbcbeb82b1af6ffa11f809b2df7d99c4f0`. Counts describe each evaluation support; the same recordings recur across shifts and methods, so table rows must not be summed as independent observations. The abstract reports paired differences; decoder tables show marginal estimates.


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


The selective decoder loses both trial-event and window recall against static LDA in every shift, and the paired intervals remain below no difference. Its coverage is markedly lower. Person and electrode operating points emit fewer false commands than static LDA, but those reductions occur alongside missed gestures and heavy rejection. In the session condition, the observed false-command rate cannot distinguish the methods.

The retained hysteresis interval-overlap novelty stop fired: True. The person coverage-failure stop fired: False. The novelty stop is a conservative rule for withdrawing a claim, not an equivalence test. Reduced output does not establish superiority or recall preservation.

## What the result does and does not show

The evidence is a negative result at the evaluated operating points. The repaired scoring and audit trail can be reused. Decoder novelty remains withdrawn; broader benchmark novelty is unestablished.

The pilot is small and uses a single dataset from healthy adults in seated laboratory conditions. Bootstrap intervals cannot compensate for the limited participant pool or shared fold training. Trial-event detection neither measures physiological onset delay nor guarantees sustained correct control. Reported p95 latency times `decoder.predict` only; it excludes feature extraction, acquisition and end-to-end command response.

The electrode condition is a proxy with preserved labels, not a physical displacement experiment. Rest exposure is short, and event rates expressed per hour extrapolate the observed denominator without supplying an hour of observation. Zero observed events and degenerate bootstrap intervals remain compatible with unobserved future errors.

Threshold-swept risk-coverage and matched-recall comparisons are untested. Lower accepted-window risk at much lower coverage cannot establish a better frontier. Few-shot remains unanswered; hysteresis is not an exhaustive search. No clinical suitability, deployment, adoption, population safety or best-decoder claim follows.

## Reproduction and resources

Regenerate the report from preserved results without rerunning evaluation:

```sh
python scripts/generate_report_tables.py
```

The generator supports `--check` for byte-for-byte mismatch detection. Measurements come from results; dates, finding identifiers and citation metadata come from repository records. See the [repair receipt](milestones/REPAIR_2026-10-01_REPORT.md) for regression evidence.

For a fresh data acquisition, follow [the data manifest](DATA.md) and run `bash scripts/download_pilot.sh`. The bounded downloader retrieves the upstream checksum manifest and verifies each selected waveform and header before replacing its destination. The upstream manifest remains the retrieval trust source. The preserved results contain per-file data digests for comparison with the evaluated inputs. After installing the documented development dependencies, `python scripts/run_benchmark.py` reproduces evaluation, traces, figures and generated current documents, including this report. Runtime and result provenance will then describe that new execution.

The preserved evaluation reports 20.370 s for benchmark runtime and 240.312 MiB for cumulative process peak RSS, using Python 3.11.15 and software versions `{"myoshift": "0.1.1", "numpy": "2.4.6", "scikit-learn": "1.9.1", "wfdb": "4.3.1"}`. Runtime excludes installation, downloading and document or figure generation. RSS is a process high-water mark, not isolated evaluation memory or the required compressed and swapped macOS footprint. The footprint measurement was blocked, so that resource gate remains unverified. Small RSS does not certify the governing memory cap.

## Licences and citation

Code is licensed under [Apache-2.0](../LICENSE). Written documentation, including this report, is under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Machine-readable results, prediction traces and figures are under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See [NOTICE](../NOTICE) for the file-scope manifest. GRABMyoFlow remains under its own CC BY 4.0 terms and must be attributed to Ehlert, Tung and Pradhan through the [dataset citation](https://doi.org/10.13026/ah52-zq51). Cite the PhysioNet platform per Pollard et al., Nature Health 2026, doi:10.1038/s44360-026-00096-z, as requested on the [official dataset page](https://physionet.org/content/grabmyo-flow/1.0.0/). Dataset terms remain applicable to the subset.

For consistent repository attribution, use [CITATION.cff](../CITATION.cff): Daneshpajouh, Amirhossein. *MyoShift: streaming sEMG benchmark and budgeted selective decoder*. Version 0.1.1, released 2026-10-01. [Repository](https://github.com/robotexlabs/myoshift). Identify this document by its title and path, `docs/negative-result-report.md`, and retain the results digest and protocol hash above when citing its negative finding. This repository report has no assigned DOI.
