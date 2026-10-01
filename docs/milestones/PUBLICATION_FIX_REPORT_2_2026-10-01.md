> Superseded historical report. Its acceptance claims do not bind the published bytes and must not be used as current verification. See [round 3](PUBLICATION_FIX_REPORT_3_2026-10-01.md) and its external commit/tree receipt. Original observations and logs are retained below.

# Publication fix report 2, 2026-10-01

Independent review `.review/PUBLISH_REVIEW_RELEASE_2026-10-01.md` (release commit `3379d04`) required fixes 1 to 5 before publication. This report records the second repair round on `main` and the rebuilt `release` orphan commit.

## Required fixes

### 1. Provenance and report gates (HIGH)

**Repair:** Source files were finalised, then `python scripts/run_benchmark.py` regenerated `results/results.json`, prediction traces, figures and all generated documents from the checkout. `python scripts/generate_documents.py --check` passes on the repaired tree.

**Evidence:** `results/results.json` provenance `source_sha256` matches current file bytes; `test_protocol_amendment_count_matches_chronology` and all `tests/test_negative_report.py` cases pass; document check exit 0.

### 2. Public history and text hygiene (HIGH)

**Repair:** Forbidden literals were removed from public docs and tests. `tests/test_release_repairs.py` builds prohibited patterns from parts (no literal vendor strings in source), scans all tracked and source paths without self-exclusion, and adds `test_public_commit_metadata_hygiene` over `git log release`. The rebuilt `release` root commit has no prohibited co-author trailers.

**Evidence:** `test_public_text_hygiene` passed; release-branch grep receipt in `results/repair_logs/round4/release_hygiene_grep.log` shows zero hits.

### 3. Verification receipts (MEDIUM)

**Repair:** This report binds exact command receipts to the repaired commit. The prior `PUBLICATION_FIX_REPORT_2026-10-01.md` overstated an all-green suite; that file is retained as historical context only.

**Evidence:** machine logs under `results/repair_logs/round4/`.

### 4. Limitations disclosure (MEDIUM)

**Repair:** `scripts/generate_documents.py` now emits a shared limitations paragraph in README, RESULTS, the technical report and the site. It states healthy-adult seated-laboratory scope, per-shift calibration allocation (50 windows per person/electrode fold, one global 50-window session prefix), unpermuted electrode calibration with permuted test features, causal offline replay and unverified footprint measurement.

**Evidence:** generated `RESULTS.md` limitations section; `test_negative_report_pipeline_and_links` passed.

### 5. Licence manifest and attribution (LOW)

**Repair:** Added `NOTICE` with file-scope licences, rights-holder notice and upstream citations. `LICENSE` appendix now names RoboteX Labs. `docs/DATA.md` records the current PhysioNet platform citation and qualifies the Meta generic neuromotor licence by inspected release.

**Evidence:** `NOTICE`; `docs/DATA.md`; negative-result report licence block.

## Verification receipt (commit-bound)

Commands run from repository root with `.venv` (Python 3.11.15, editable install `.[dev]`).

| Check | Result | Evidence |
|---|---|---|
| Non-network suite | 73 passed, 0 failed, 1 deselected (network) | `results/repair_logs/round4/full_suite.log` |
| Release commit metadata | Clean after release rebuild | `test_public_commit_metadata_hygiene` |
| Coverage | 95.02% combined | `results/repair_logs/round4/coverage.json` |
| Ruff | Clean | `results/repair_logs/round4/ruff.log` |
| mypy | Clean, 19 files | `results/repair_logs/round4/mypy.log` |
| Pyright | 0 errors, 0 warnings | `results/repair_logs/round4/pyright.log` |
| Document consistency | Passed | `python scripts/generate_documents.py --check` |
| Headless regeneration | Passed | `python scripts/run_benchmark.py` |
| Scientific scalars | Unchanged at operating points | person myoshift window recall 0.073; 92 false events total |

Peak RSS after regeneration: 240.828 MiB. Evaluation runtime: 21.031 s. Timings are machine-dependent; metric point estimates and intervals at published operating points are unchanged from the prior committed artifact.

## Deviations

Hosted GitHub Actions matrix receipt remains unverified locally. The governing compressed/swapped footprint gate is still UNVERIFIED when `top` is blocked. `main` retains full repair history; only `release` is the proposed public root commit. Frozen `docs/PREREGISTRATION.md` bytes were not edited; Meta licence qualification appears in `NOTICE` and `docs/DATA.md` only.
