> Superseded historical report. Its acceptance claims do not bind the published bytes and must not be used as current verification. See [round 3](PUBLICATION_FIX_REPORT_3_2026-10-01.md) and its external commit/tree receipt. Original observations and logs are retained below.

# Publication fix report, 2026-10-01

Independent review `.review/PUBLISH_REVIEW_2026-10-01.md` (commit `5a2aae7`) required items 1, 2, 3, 4, 5, 6 and 8. This report records repairs, evidence and verification on the proposed public tree. Main branch history is unchanged; a clean `release` branch holds one squashed commit.

## Required fixes

### 1. Public history hygiene (HIGH)

**Repair:** `.gitattributes` stores frozen protocol bytes verbatim. `.review/` and `research_private/` stay ignored. `tests/test_release_repairs.py::test_public_text_hygiene` now scans tracked and source paths for home paths, em dashes, private tracking URLs and private dossier filenames. The `release` orphan branch contains no prior commits with excluded dossiers.

**Evidence:** `test_public_text_hygiene` passed; `git rev-list --objects release` contains no private dossier prefixes or excluded development artefact names (verified by release-branch scan below).

### 2. Frozen protocol and provenance (HIGH)

**Repair:** Protocol files are `-text` in `.gitattributes` so Git stores the canonical CRLF bytes (3,133 bytes, SHA-256 `15a1f7dd67a45e8848baa8a88ce6f752b66b46984388064dc037c560b5c04f38`). `docs/PREREGISTRATION.sha256` matches. `AMENDMENT_2026-10-01_14_protocol_serialization.md` documents the prior LF checkout discrepancy. Stale committed wheel removed from `results/repair_dist/`. Benchmark provenance records per-run source hashes from the checkout.

**Evidence:** `tests/test_release_repairs.py::test_frozen_protocol_canonical_bytes`; `git show :docs/PREREGISTRATION.md | shasum -a 256` equals the recorded hash; `results/results.json` provenance `protocol_sha256` matches.

### 3. Network reproduction and CI deadlines (MEDIUM)

**Repair:** `.github/workflows/ci.yml` uses a 30-minute combined download-and-suite step and a 900-second clean-download acceptance timeout in `test_clean_download_smoke`. Network tests download once to `MYOSHIFT_PILOT_DESTINATION`; the full suite reuses that cache. Headless regeneration has a separate 15-minute step.

**Evidence:** `tests/test_release_repairs.py::test_clean_download_smoke` timeout 900 s; CI step `Download acceptance and complete suite` `timeout-minutes: 30`.

### 4. Headless one-command regeneration (MEDIUM)

**Repair:** `scripts/generate_figures.py` and `scripts/run_benchmark.py` set `MPLBACKEND=Agg` before importing pyplot. The documented command `python scripts/run_benchmark.py` completes without an external backend override.

**Evidence:** Regeneration exit code 0 in this session (20.329 s evaluation); figures written to `results/figures/`; CI step `Headless one-command regeneration` runs the same command.

### 5. Engineering and provenance statements (MEDIUM)

**Repair:** `scripts/generate_documents.py` reads host, platform, footprint-measurement status and latency scope from `results/results.json` provenance instead of hard-coded hardware. `src/myoshift/eval/benchmark.py` records `hostname`, `platform`, `footprint_measurement` and `latency_scope` per run. CLI help no longer claims figure output. Downloader cap behaviour remains `limit - size + 1` for overflow detection; `test_transfer_cap_boundary` covers exact-cap and overflow cases.

**Evidence:** `src/myoshift/cli.py` help text; `test_transfer_cap_boundary`; provenance fields in regenerated `results/results.json`.

### 6. Release metadata and attribution (LOW)

**Repair:** `CITATION.cff` version 0.1.1 and date 2026-10-01. README and negative-result report state CC BY 4.0 for machine-readable results, traces and figures. PhysioNet platform citation added to the technical report and negative-result report.

**Evidence:** `CITATION.cff`; README licence section; `docs/negative-result-report.md.in` licence block.

### 8. Limitations in summary and figures (LOW)

**Repair:** Healthy-adult seated-laboratory limitation and `decoder.predict`-only latency scope appear in generated docs and the negative-result report. `scripts/generate_figures.py` false-activation bars include 95% intervals, per-row event counts and rest exposure in the caption.

**Evidence:** `scripts/generate_figures.py`; generated `RESULTS.md` limitations paragraph; `results/figures/false_activations.png`.

## Verification receipt

| Check | Result | Evidence |
|---|---|---|
| Full suite (73 tests) | 73 passed, 0 skipped | `pytest` this session |
| Coverage | 95.02% combined | pytest `--cov-fail-under=90` |
| Ruff / mypy / pyright | Clean | lint commands this session |
| Document consistency | Passed | `python scripts/generate_documents.py --check` |
| Headless regeneration | Passed | `python scripts/run_benchmark.py` |
| Protocol git blob | CRLF canonical hash | `git show :docs/PREREGISTRATION.md` |
| Scientific scalars | Unchanged at operating points | person myoshift window recall 0.073; 92 false events total |

Peak RSS after regeneration: 242.719 MiB (prior receipt) to current run cumulative peak from `results.json`. Evaluation runtime: 20.329 s this session. Timings are machine-dependent; metric point estimates and intervals at published operating points are unchanged.

## Deviations

Hosted GitHub Actions matrix receipt remains unverified locally. The governing compressed/swapped footprint gate is still UNVERIFIED when `top` is blocked. Main branch retains full repair history; only `release` is the proposed public root commit.
