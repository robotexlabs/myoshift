# MyoShift

RoboteX Labs' public-data engineering demonstration of reproducible sEMG command-event evaluation under participant, session and proxy electrode shifts. The reusable capability is an audited data-to-report pipeline: verified inputs, leakage-aware splits, record resets, measured rest exposure and participant uncertainty. This corrected negative study provides no evidence of client delivery, paid firm past performance, adoption or clinical benefit.

![Person-shift risk and coverage operating points](results/figures/risk_coverage_person.png)

Each annotated point is one fixed operating point, not a measured frontier. Four healthy seated participants, heavy abstention and short rest exposure limit interpretation; zero counts cannot establish safety.

Person-shift selective window recall is lower than static LDA: 0.073 [0.031, 0.137] versus 0.512 [0.381, 0.751]. Trial-event recall is a separate, coarse detection metric, not physiological event timing. The available runs counted 92 false command events in total across the repeated method evaluations. Short laboratory rest exposure and a zero-count bootstrap interval cannot establish safety equivalence. Decoder novelty remains withdrawn. Threshold-swept risk-coverage and matched-recall comparisons are untested. Person coverage stop rule fired: False. Hysteresis interval-overlap novelty stop fired: True. This withdrawal stop is not an equivalence test. The few-shot baseline is unavailable under the frozen rest-only calibration prefix. No general benchmark novelty or clinical usefulness is established by this repair.

## Quick start

These commands work on a fresh clone. The download script fetches the 96 public GRABMyoFlow pilot records from PhysioNet and checks every SHA-256; everything after it runs offline.

```sh
git clone https://github.com/robotexlabs/myoshift.git
cd myoshift
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
bash scripts/download_pilot.sh
python scripts/run_benchmark.py
myoshift verify-scorers
python scripts/generate_documents.py --check
python -m pytest -o addopts= -m 'not network' --cov=myoshift --cov-fail-under=90
```

The single benchmark command regenerates JSON, traces, figures and current documents headlessly from downloaded public data. Without the download, the benchmark and the data-bound tests cannot run. PhysioNet can be slow: if the download stops with a read timeout, run it again. On 2026-10-18 it needed four runs. The network test needs internet access and an empty destination; cached acceptance is recorded separately. Python 3.11 on macOS arm64 is locally exercised; Python 3.12 is configured in CI and awaits a hosted receipt. No other platform is validated.

CLI example: `myoshift verify-scorers`; library entry: `myoshift.eval.benchmark.run_full_benchmark(data_root, output_dir)`.

## What you get

MyoShift is a research prototype, not a medical device. On 2026-10-18 the quick start printed these lines, among others:

```text
Verified 96 records; 35032550 transferred bytes including manifest
Results written to results/results.json
Scorer verification passed
```

The benchmark writes `results/results.json`, prediction traces in `results/predictions.jsonl` and two figures, [risk and coverage](results/figures/risk_coverage_person.png) and [false command events](results/figures/false_activations.png). It also regenerates RESULTS.md, this README, the technical report, the negative-result report and a static summary page, [docs/site/index.html](docs/site/index.html), which you can open in a browser from your clone.

Person-shift results from `results/results.json`, with 95% participant-cluster intervals:

| Decoder | Trial-event recall | Window recall | Coverage | False events/rest hour |
|---|---|---|---|---|
| static_lda | 0.819 [0.694, 0.944] | 0.512 [0.381, 0.751] | 1.000 [1.000, 1.000] | 912.626 [0.000, 2636.475] |
| hysteresis | 0.750 [0.611, 0.917] | 0.473 [0.347, 0.696] | 1.000 [1.000, 1.000] | 608.417 [0.000, 1723.849] |
| few_shot | unavailable | | | |
| myoshift | 0.333 [0.153, 0.597] | 0.073 [0.031, 0.137] | 0.074 [0.043, 0.108] | 0.000 [0.000, 0.000] |

These are fixed operating points from four healthy seated participants. They do not show safety, adoption or clinical benefit.

## Inspect the evidence

[Compact verification receipt](docs/milestones/PUBLICATION_FIX_REPORT_3_2026-10-01.md), [full results and limitations](RESULTS.md), [negative-result report](docs/negative-result-report.md), [technical report](docs/technical-report.md). Frozen protocol bytes are preserved; the chronology of a pre-result freeze remains unverified.

Related work: [EMGBench](https://arxiv.org/abs/2410.23625), [generic neuromotor interface](https://doi.org/10.1038/s41586-025-09255-w). Data: [GRABMyoFlow](https://physionet.org/content/grabmyo-flow/1.0.0/). No omission or superiority over these resources is claimed.

## Licence and citation

Code: [Apache-2.0](LICENSE). Documentation and derived results: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See [NOTICE](NOTICE) for exhaustive scopes and upstream credit, and [CITATION.cff](CITATION.cff).
