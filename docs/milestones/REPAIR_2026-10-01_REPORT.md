# Repair report: 2026-10-01 round

All scoped regression oracles failed before repair (13 failed, `results/repair_logs/regressions_before_validated.log`), then passed after repair. Protocol changes are retrospective: results had already been seen. The filename date is the requested repair-round label, not an immutable timestamp.

| Finding | Status and change | Implementation | Regression tests in tests/test_repairs.py | Amendment |
|---|---|---|---|---|
| 1 | Fixed within scope. Strict complete identity mapping and invariant labels/rest flags. | `src/myoshift/eval/benchmark.py:85` | `test_f01_full_identity_mapping`, `test_f01_real_electrode_probe` | `docs/amendments/AMENDMENT_2026-10-01_01_identity_mapping.md` |
| 2 | Fixed within scope. Count command onsets; measure clipped decision exposure; missing exposure is null. | `src/myoshift/eval/metrics.py:41` | `test_f02_held_event_stride_and_unavailable_exposure`, `test_f02_event_offset_change_and_actual_exposure` | `docs/amendments/AMENDMENT_2026-10-01_02_command_events_exposure.md` |
| 3 | Fixed within scope. Pool sufficient statistics before each metric-specific ratio. | `src/myoshift/eval/metrics.py:164` | `test_f03_production_perfect_empty_and_ratio_counterexample`, `test_f03_metric_specific_eligibility_and_wholly_abstained_trial` | `docs/amendments/AMENDMENT_2026-10-01_03_ratio_aggregation.md` |
| 4 | Fixed within scope. Purge shared raw support and reset decoder state at independent trials. | `src/myoshift/eval/splits.py:83` | `test_f04_raw_support_purged_and_trial_state_reset`, `test_f04_both_split_boundaries_and_unknown_support` | `docs/amendments/AMENDMENT_2026-10-01_04_purge_and_reset.md` |
| 5 | Fixed within scope. All-participant hold-out folds, paired participant bootstrap, conditional/descriptive wording; frontier untested. | `src/myoshift/eval/metrics.py:189` | `test_f05_participant_bootstrap_and_paired_differences`, `test_f05_cluster_draws_keep_repeated_trials_and_labels` | `docs/amendments/AMENDMENT_2026-10-01_05_participant_uncertainty.md` |
| 6 | Fixed within scope. Independent empirical calibration with consistent confidence score; cancelled normalisation removed. | `src/myoshift/models/selective_decoder.py:36` | `test_f06_independent_calibration_consistent_score`, `test_f06_calibration_required_and_source_information_budget` | `docs/amendments/AMENDMENT_2026-10-01_06_independent_selective_calibration.md` |
| 7 | Fixed within scope. Rest-only few-shot is unavailable, with no fallback. Equal source-informed information budgets. | `src/myoshift/eval/benchmark.py:53` | `test_f07_few_shot_never_falls_back` | `docs/amendments/AMENDMENT_2026-10-01_07_unavailable_few_shot_equal_budget.md` |
| 8 | Fixed within scope. Named W1-W12 selection and separate within-ring permutation. | `src/myoshift/data/grabmyo.py:84` | `test_f08_wrist_channels_and_ring_shift`, `test_f08_verified_channel_names_and_invalid_ring` | `docs/amendments/AMENDMENT_2026-10-01_08_verified_wrist_ring_channels.md` |
| 9 | Fixed within scope. One-command regenerated JSON, figures and current documents, with a mismatch gate. | `scripts/generate_documents.py:15` | `test_f09_generated_document_mismatch`, `test_f09_repair_report_links_each_numbered_amendment` | `docs/amendments/AMENDMENT_2026-10-01_09_generated_reporting.md` |
| 11 | Fixed within scope. Typed dependency boundaries, restored diagnostics, no unused import, isolated wheel CI steps. | `src/myoshift/_external.py:19` | `test_f11_strict_diagnostics_and_wheel_ci` | `docs/amendments/AMENDMENT_2026-10-01_10_strict_engineering.md` |
| 13 | Fixed within scope. Positive CLI/library dimensions and non-negative calibration budget; RSS/latency budget checks. | `src/myoshift/types.py:39` | `test_f13_cli_integer_validation`, `test_f13_library_integer_and_existing_runtime_budgets` | `docs/amendments/AMENDMENT_2026-10-01_11_integer_validation.md` |

Additional anchors: `src/myoshift/eval/benchmark.py:108`, `src/myoshift/eval/benchmark.py:126`, `src/myoshift/features/extract.py:32`, `pyrightconfig.json:8`, `.github/workflows/ci.yml:35`, `src/myoshift/cli.py:33`.

Additional amendment: docs/amendments/AMENDMENT_2026-10-01_12_retained_novelty_stop.md. The original conservative interval-overlap novelty stop is retained; fired: True. Regression: test_f05_original_novelty_stop_is_retained.

## Old versus corrected headlines

Old event recall was a mean of per-trial window ratios, with ineligible trial zeros. It is not comparable to corrected trial-event recall. The new window-recall column makes the metric change explicit. Old person/electrode results held out one participant; the new results hold out each available participant. Original electrode labels were corrupted, so those numbers have no scientific interpretation.

| Shift / method | Old reported recall [interval] | New trial-event recall [interval] | New window recall [interval] | Old n test | New n test / gesture events / participants |
|---|---|---|---|---:|---|
| person/static_lda | 0.306 [0.161, 0.484] | 0.819 [0.694, 0.944] | 0.512 [0.381, 0.751] | 2878 | 11492 / 72 / 4 |
| person/hysteresis | 0.282 [0.145, 0.458] | 0.750 [0.611, 0.917] | 0.473 [0.347, 0.696] | 2878 | 11492 / 72 / 4 |
| person/few_shot | 0.306 [0.161, 0.484] | unavailable | unavailable | 2878 | unavailable |
| person/myoshift | 0.183 [0.055, 0.344] | 0.333 [0.153, 0.597] | 0.073 [0.031, 0.137] | 2878 | 11492 / 72 / 4 |
| session/static_lda | 0.543 [0.384, 0.694] | 0.958 [0.875, 1.000] | 0.724 [0.463, 0.944] | 3854 | 3849 / 24 / 4 |
| session/hysteresis | 0.536 [0.380, 0.692] | 0.750 [0.456, 1.000] | 0.695 [0.431, 0.913] | 3854 | 3849 / 24 / 4 |
| session/few_shot | 0.543 [0.384, 0.694] | unavailable | unavailable | 3854 | unavailable |
| session/myoshift | 0.457 [0.306, 0.614] | 0.458 [0.250, 0.708] | 0.217 [0.084, 0.287] | 3854 | 3849 / 24 / 4 |
| electrode/static_lda | 0.242 [0.003, 0.556] | 0.472 [0.375, 0.528] | 0.227 [0.134, 0.314] | 2878 | 11492 / 72 / 4 |
| electrode/hysteresis | 0.199 [0.000, 0.496] | 0.444 [0.326, 0.528] | 0.201 [0.111, 0.282] | 2878 | 11492 / 72 / 4 |
| electrode/few_shot | 0.242 [0.003, 0.556] | unavailable | unavailable | 2878 | unavailable |
| electrode/myoshift | 0.067 [0.000, 0.194] | 0.111 [0.069, 0.139] | 0.017 [0.005, 0.036] | 2878 | 11492 / 72 / 4 |

| Shift / method | Old risk [interval] | New risk [interval] | Old coverage [interval] | New coverage [interval] | Old reported false/hour [interval] | New false events/hour [interval] | Rest seconds |
|---|---|---|---|---|---|---|---:|
| person/static_lda | 0.444 [0.261, 0.625] | 0.398 [0.192, 0.523] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 912.626 [0.000, 2636.475] | 106.505859 |
| person/hysteresis | 0.468 [0.290, 0.646] | 0.423 [0.233, 0.540] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 608.417 [0.000, 1723.849] | 106.505859 |
| person/myoshift | 0.696 [0.490, 0.861] | 0.239 [0.008, 0.589] | 0.304 [0.168, 0.461] | 0.074 [0.043, 0.108] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 106.505859 |
| session/static_lda | 0.207 [0.079, 0.339] | 0.210 [0.043, 0.403] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 36.227051 |
| session/hysteresis | 0.214 [0.083, 0.346] | 0.232 [0.067, 0.426] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 36.227051 |
| session/myoshift | 0.441 [0.285, 0.598] | 0.003 [0.000, 0.009] | 0.513 [0.367, 0.664] | 0.166 [0.064, 0.220] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 36.227051 |
| electrode/static_lda | 0.758 [0.444, 0.997] | 0.611 [0.524, 0.685] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 878.825 [0.000, 2636.475] | 106.505859 |
| electrode/hysteresis | 0.801 [0.504, 1.000] | 0.625 [0.549, 0.699] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 676.019 [0.000, 2028.057] | 106.505859 |
| electrode/myoshift | 0.804 [0.478, 1.000] | 0.581 [0.052, 0.901] | 0.095 [0.011, 0.219] | 0.031 [0.011, 0.053] | 0.000 [0.000, 0.000] | 33.801 [0.000, 101.403] | 106.505859 |

Decoder novelty remains withdrawn. Zero-event results in some conditions and [0,0] bootstrap intervals do not establish safety equivalence. Trial-event recall is coarse and can saturate despite poor window recall. Full interpretations and paired contrasts are generated in RESULTS.md. Threshold-swept and matched-recall comparisons are untested.

## Commands and engineering gates

| Command receipt | Exact argv | Exit | Seconds | Child RSS MiB | Source changed during run | Log |
|---|---|---:|---:|---:|---|---|
| artifact_integrity | `[".venv/bin/python", "results/repair_logs/artifact_integrity_probe.txt"]` | 0 | 2.882 | 275.703125 | [] | `results/repair_logs/artifact_integrity.log` |
| artifact_integrity_final | `[".venv/bin/python", "results/repair_logs/artifact_integrity_probe.txt"]` | 0 | 3.110 | 276.140625 | [] | `results/repair_logs/artifact_integrity_final.log` |
| artifact_release | `[".venv/bin/python", "results/repair_logs/artifact_integrity_probe.txt"]` | 0 | 2.869 | 275.59375 | [] | `results/repair_logs/artifact_release.log` |
| ci_final | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "tests/test_repairs.py::test_f11_strict_diagnostics_and_wheel_ci", "-q"]` | 0 | 1.379 | 165.234375 | [] | `results/repair_logs/ci_final.log` |
| ci_regression | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "tests/test_repairs.py::test_f11_strict_diagnostics_and_wheel_ci", "-q"]` | 0 | 1.488 | 164.46875 | [] | `results/repair_logs/ci_regression.log` |
| corrected_evaluation | `[".venv/bin/python", "scripts/run_benchmark.py"]` | 0 | 40.732 | unavailable | [] | `results/repair_logs/corrected_evaluation.log` |
| docs_release | `[".venv/bin/python", "scripts/generate_documents.py", "--check"]` | 0 | 0.114 | 20.671875 | [] | `results/repair_logs/docs_release.log` |
| document_consistency | `[".venv/bin/python", "scripts/generate_documents.py", "--check"]` | 0 | 0.111 | 20.609375 | [] | `results/repair_logs/document_consistency.log` |
| evaluation_final | `[".venv/bin/python", "scripts/run_benchmark.py"]` | 0 | 38.329 | 280.5625 | [] | `results/repair_logs/evaluation_final.log` |
| evaluation_release | `[".venv/bin/python", "scripts/run_benchmark.py"]` | 0 | 39.427 | 291.375 | [] | `results/repair_logs/evaluation_release.log` |
| evaluation_verified | `[".venv/bin/python", "scripts/run_benchmark.py"]` | 0 | 38.201 | 286.59375 | [] | `results/repair_logs/evaluation_verified.log` |
| full_suite | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "--cov=myoshift", "--cov-report=term-missing", "--cov-report=json:results/repair_logs/coverage.json", "--cov-report=xml:results/repair_logs/coverage.xml", "--cov-fail-under=90", "-q"]` | 1 | 119.854 | unavailable | ['tests/test_features.py'] | `results/repair_logs/full_suite.log` |
| full_suite_final | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "--cov=myoshift", "--cov-report=term-missing", "--cov-report=json:results/repair_logs/coverage.json", "--cov-report=xml:results/repair_logs/coverage.xml", "--cov-fail-under=90", "-q"]` | 0 | 122.230 | unavailable | [] | `results/repair_logs/full_suite_final.log` |
| full_suite_final_ledger | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "--cov=myoshift", "--cov-report=term-missing", "--cov-report=json:results/repair_logs/coverage.json", "--cov-report=xml:results/repair_logs/coverage.xml", "--cov-fail-under=90", "-q"]` | 0 | 119.147 | 261.390625 | [] | `results/repair_logs/full_suite_final_ledger.log` |
| full_suite_interim | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "--cov=myoshift", "--cov-report=term-missing", "--cov-report=json:results/repair_logs/coverage_interim.json", "--cov-fail-under=90", "-q"]` | 1 | 386.119 | unavailable | not measured in early attempts | `results/repair_logs/full_suite_interim.log` |
| full_suite_release | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "--cov=myoshift", "--cov-report=term-missing", "--cov-report=json:results/repair_logs/coverage.json", "--cov-report=xml:results/repair_logs/coverage.xml", "--cov-fail-under=90", "-q"]` | 0 | 120.546 | 256.40625 | [] | `results/repair_logs/full_suite_release.log` |
| full_suite_verified | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "--cov=myoshift", "--cov-report=term-missing", "--cov-report=json:results/repair_logs/coverage.json", "--cov-report=xml:results/repair_logs/coverage.xml", "--cov-fail-under=90", "-q"]` | 0 | 118.767 | 263.921875 | [] | `results/repair_logs/full_suite_verified.log` |
| install_builder | `[".venv/bin/python", "-m", "pip", "install", "build"]` | 0 | 1.160 | unavailable | not measured in early attempts | `results/repair_logs/install_builder.log` |
| ledger_before | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "tests/test_repairs.py::test_f09_repair_report_links_each_numbered_amendment", "-q"]` | 1 | 2.149 | 165.9375 | [] | `results/repair_logs/ledger_before.log` |
| mypy | `[".venv/bin/mypy", "src"]` | 0 | 0.224 | unavailable | not measured in early attempts | `results/repair_logs/mypy.log` |
| mypy_final | `[".venv/bin/mypy", "src"]` | 0 | 0.329 | 47.71875 | [] | `results/repair_logs/mypy_final.log` |
| mypy_interim | `[".venv/bin/mypy", "src"]` | 1 | 0.544 | unavailable | not measured in early attempts | `results/repair_logs/mypy_interim.log` |
| mypy_release | `[".venv/bin/mypy", "src"]` | 0 | 0.517 | 86.9375 | [] | `results/repair_logs/mypy_release.log` |
| mypy_verified | `[".venv/bin/mypy", "src"]` | 0 | 0.214 | 85.96875 | [] | `results/repair_logs/mypy_verified.log` |
| pyright | `[".venv/bin/pyright", "src"]` | 0 | 1.611 | unavailable | not measured in early attempts | `results/repair_logs/pyright.log` |
| pyright_final | `[".venv/bin/pyright", "src"]` | 0 | 1.500 | 263.75 | [] | `results/repair_logs/pyright_final.log` |
| pyright_interim | `[".venv/bin/pyright", "src"]` | 0 | 1.388 | unavailable | not measured in early attempts | `results/repair_logs/pyright_interim.log` |
| pyright_release | `[".venv/bin/pyright", "src"]` | 1 | 1.554 | 266.1875 | [] | `results/repair_logs/pyright_release.log` |
| pyright_verified | `[".venv/bin/pyright", "src"]` | 0 | 1.565 | 267.4375 | [] | `results/repair_logs/pyright_verified.log` |
| regressions_after | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "tests/test_repairs.py", "-q"]` | 0 | 6.322 | unavailable | not measured in early attempts | `results/repair_logs/regressions_after.log` |
| regressions_before_validated | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "tests/test_repairs.py", "-q"]` | 1 | 10.125 | unavailable | not measured in early attempts | `results/repair_logs/regressions_before_validated.log` |
| regressions_extended | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "tests/test_repairs.py", "-q"]` | 1 | 21.592 | unavailable | not measured in early attempts | `results/repair_logs/regressions_extended.log` |
| regressions_stable | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "tests/test_repairs.py", "-q"]` | 0 | 22.505 | unavailable | [] | `results/repair_logs/regressions_stable.log` |
| repair_report | `[".venv/bin/python", "scripts/generate_repair_report.py"]` | 0 | 0.108 | 20.71875 | [] | `results/repair_logs/repair_report.log` |
| repair_report_final | `[".venv/bin/python", "scripts/generate_repair_report.py"]` | 0 | 0.107 | 20.53125 | [] | `results/repair_logs/repair_report_final.log` |
| repair_report_preflight | `[".venv/bin/python", "scripts/generate_repair_report.py"]` | 0 | 0.106 | 20.578125 | [] | `results/repair_logs/repair_report_preflight.log` |
| report_ledger_final | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "tests/test_repairs.py::test_f09_repair_report_links_each_numbered_amendment", "-q"]` | 0 | 1.395 | 165.078125 | [] | `results/repair_logs/report_ledger_final.log` |
| report_regressions | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "tests/test_repairs.py::test_f09_generated_document_mismatch", "tests/test_repairs.py::test_f11_strict_diagnostics_and_wheel_ci", "-q"]` | 0 | 1.940 | 167.21875 | [] | `results/repair_logs/report_regressions.log` |
| ruff | `[".venv/bin/ruff", "check", "."]` | 0 | 0.109 | unavailable | [] | `results/repair_logs/ruff.log` |
| ruff_final | `[".venv/bin/ruff", "check", "."]` | 0 | 0.110 | 22.8125 | [] | `results/repair_logs/ruff_final.log` |
| ruff_verified | `[".venv/bin/ruff", "check", "."]` | 0 | 0.110 | 22.890625 | [] | `results/repair_logs/ruff_verified.log` |
| stop_rule_after | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "tests/test_repairs.py::test_f05_original_novelty_stop_is_retained", "-q"]` | 0 | 2.067 | 165.578125 | [] | `results/repair_logs/stop_rule_after.log` |
| stop_rule_before | `[".venv/bin/python", "-m", "pytest", "-o", "addopts=", "tests/test_repairs.py::test_f05_original_novelty_stop_is_retained", "-q"]` | 1 | 2.383 | 165.375 | [] | `results/repair_logs/stop_rule_before.log` |
| typing_before | `[".venv/bin/pyright", "src"]` | 1 | 1.575 | unavailable | not measured in early attempts | `results/repair_logs/typing_before.log` |
| wheel_build | `[".venv/bin/python", "-m", "build", "--wheel", "--outdir", "results/repair_dist"]` | 1 | 0.124 | unavailable | not measured in early attempts | `results/repair_logs/wheel_build.log` |
| wheel_build_documented | `[".venv/bin/python", "-m", "build", "--wheel", "--outdir", "results/repair_dist"]` | 0 | 1.905 | 65.734375 | [] | `results/repair_logs/wheel_build_documented.log` |
| wheel_build_final | `[".venv/bin/python", "-m", "build", "--wheel", "--outdir", "results/repair_dist"]` | 0 | 2.116 | unavailable | [] | `results/repair_logs/wheel_build_final.log` |
| wheel_build_final_ledger | `[".venv/bin/python", "-m", "build", "--wheel", "--outdir", "results/repair_dist"]` | 0 | 2.084 | 66.0 | [] | `results/repair_logs/wheel_build_final_ledger.log` |
| wheel_build_release | `[".venv/bin/python", "-m", "build", "--wheel", "--outdir", "results/repair_dist"]` | 0 | 1.979 | 65.546875 | [] | `results/repair_logs/wheel_build_release.log` |
| wheel_build_verified | `[".venv/bin/python", "-m", "build", "--wheel", "--outdir", "results/repair_dist"]` | 0 | 1.756 | 65.8125 | [] | `results/repair_logs/wheel_build_verified.log` |
| wheel_install | `[".venv/bin/python", "scripts/check_wheel.py"]` | 0 | 25.033 | unavailable | [] | `results/repair_logs/wheel_install.log` |
| wheel_install_documented | `[".venv/bin/python", "scripts/check_wheel.py"]` | 0 | 23.472 | 259.609375 | [] | `results/repair_logs/wheel_install_documented.log` |
| wheel_install_release | `[".venv/bin/python", "scripts/check_wheel.py"]` | 0 | 22.060 | 252.1875 | [] | `results/repair_logs/wheel_install_release.log` |
| wheel_install_verified | `[".venv/bin/python", "scripts/check_wheel.py"]` | 0 | 23.491 | 253.921875 | [] | `results/repair_logs/wheel_install_verified.log` |
| wheel_release | `[".venv/bin/python", "-m", "build", "--wheel", "--outdir", "results/repair_dist"]` | 0 | 1.814 | 65.546875 | [] | `results/repair_logs/wheel_release.log` |

Full branch-inclusive library coverage: 95.47%.
- person/static_lda: 1.633 s; cumulative RSS 214.516 MiB.
- person/hysteresis: 1.711 s; cumulative RSS 218.078 MiB.
- person/myoshift: 1.621 s; cumulative RSS 221.828 MiB.
- session/static_lda: 0.564 s; cumulative RSS 225.000 MiB.
- session/hysteresis: 0.555 s; cumulative RSS 225.000 MiB.
- session/myoshift: 0.547 s; cumulative RSS 225.438 MiB.
- electrode/static_lda: 1.636 s; cumulative RSS 230.078 MiB.
- electrode/hysteresis: 1.682 s; cumulative RSS 234.250 MiB.
- electrode/myoshift: 1.620 s; cumulative RSS 237.938 MiB.

Full evaluation: 21.395 s; cumulative process peak RSS 241.109 MiB. RSS includes prior folds and is not isolated per-run memory or macOS compressed/swapped footprint. Every command receipt records attempted top measurement. The sandbox rejects top, so no peak footprint claim or under-12-GB footprint certification is made. Foreground commands use recorded timeouts. No hosted CI execution is claimed.

Frozen preregistration and hash bytes unchanged: True. Evaluation source hashes match current files: True. Hashes prove byte consistency only; pre-result chronology remains unverified. Source/data hashes and exact installed dependency versions are in results/results.json.

Deviations: top footprint gate could not be verified because execution is denied by the sandbox. Finding 5 uses the expressly permitted untested-frontier route. Finding 7 uses the expressly permitted unavailable-baseline route. Findings 10, 12 and the downloader portion of 13 were outside the repair packet; no immutable freeze receipt, second dataset, official external controller or hosted CI run is supplied. Existing input research records remain historical source evidence. Concurrent edits were observed during early checks; affected interim runs are not final gate evidence. Final command receipts record source hashes before and after each run.


## Release repair round, 2026-10-01

This section supersedes the earlier scope exclusions for the downloader, public inputs and resource-rule reconciliation. Results had already been seen. The frozen protocol is unchanged; its chronology remains unverified.

1. The shell entry point now uses LF endings and retrieves the official SHA256SUMS.txt manifest through the bounded Python downloader. A clean temporary-destination network check covers the real 96-record pilot.
2. Transfers enforce a 4 MiB per-file cap and a 64 MiB aggregate cap including the manifest, with a 120-second file deadline and bounded socket waits. SHA-256 is updated incrementally; a verified same-directory temporary file is atomically promoted only after success. Interrupted, corrupt and oversized payload regressions preserve existing evidence and clean temporary files. Aggregate exhaustion is separately tested.
3. FIX_REPORT_2026-09-30.md is explicitly superseded. Its incompatible intervals, event rates and engineering counts are withdrawn; the original remains private. CHANGELOG.md describes the retrospective participant-cluster repair. Historical receipts are bound to their original result digest in results/repair_logs/historical_binding.json and are not relabelled as current validation.
4. The benchmark resolves checkout provenance from the installed module location and bundles protocol resources for wheel installations. It reads these before feature extraction. The library regression changes to a temporary working directory; the isolated-wheel check also executes the full benchmark there with an absolute data location and a temporary output location. Provenance keys remain relative.
5. Original dossiers and the internal audit are preserved in ignored research_private/. The public research context contains neutral scope statements and resolved primary references. It withdraws inherited multi-project novelty assertions. Required scholarly and dataset credit remains in the technical references.
6. AMENDMENT_2026-10-01_13_resource_cap.md retrospectively makes the stricter 8 GB process footprint cap govern all phases. The frozen 12 GB rule remains in the record. Default 2,048 MiB RSS checks are a different measurement and do not continuously cover feature extraction. Compressed/swapped peak footprint remains UNVERIFIED.

Public historical repair receipts now use repository-relative paths. Their exact originals remain private. The public text regression reads index entries without repository management commands and also scans newly added public source, tests, scripts, documentation and receipt files for home paths and prohibited punctuation.

### Validation receipts for this round

The complete suite passed 62 tests with zero skips or deselections and 95.09% branch-inclusive library coverage, including the real shell command downloading all 96 pilot records to a clean temporary destination. The first attempt rejected the upstream 3,421,720-byte manifest against an overly small allowance; the corrected 4 MiB allowance passed. That failed attempt remains an interim receipt, not final gate evidence.

After aligning the repair version identifier to 0.1.1, all 61 local tests were repeated and passed with the same 95.09% coverage; the network test was deselected only in this additional run. The complete earlier network gate remains recorded separately. The wheel was freshly built and installed, its scorer and full benchmark passed from an unrelated temporary working directory, and its version and bundled frozen protocol bytes were checked.

| Gate | Exit | Command wall seconds | Receipt |
|---|---:|---:|---|
| Complete suite including network | 0 | 595.921 | results/repair_logs/round2_full_suite_final.json |
| Post-version local suite | 0 | 119.036 | results/repair_logs/round2_post_version_suite.json |
| Ruff | 0 | 0.110 | results/repair_logs/round2_ruff_final.json |
| Mypy | 0 | 0.315 | results/repair_logs/round2_mypy_final.json |
| Pyright | 0 | 1.473 | results/repair_logs/round2_pyright_final.json |
| Wheel build | 0 | 1.676 | results/repair_logs/round2_wheel_build.json |
| Fresh wheel install and portable API | 0 | 56.534 | results/repair_logs/round2_wheel_install.json |
| Final evaluation and table regeneration | 0 | 38.562 | results/repair_logs/round2_evaluation_final.json |
| Generated-document consistency | 0 | 0.111 | results/repair_logs/round2_docs_final.json |

Scientific comparison: all 225 metric point/interval scalars, all remaining scientific run fields including counts/exposure, paired comparisons, configuration and stop rules are unchanged. The prediction trace is byte-identical. Figures and the four current table documents were regenerated. Timing, RSS and provenance are allowed to refresh. The comparison is in results/repair_logs/round2_scientific_comparison.json, bound to the before/after result digests.

Current evaluation timer: 21.181 seconds; cumulative process peak RSS: 242.719 MiB. Neither the library RSS value nor child-process RSS receipts certify compressed/swapped peak footprint. The governing 8 GB footprint gate remains UNVERIFIED. No prospective chronology, hosted CI execution or publication receipt is claimed.

All commands remained foreground jobs with bounded timeouts. No repository management commands were invoked. No scientific feature, fitting, decoding, scoring or uncertainty algorithm was changed in this round. Exact original input dossiers, withdrawn report and pre-normalization receipts remain in the ignored private evidence folder.

The cap limits accepted payload bytes and bytes written to the temporary file. The downloader reads at most one additional detection byte before rejecting an oversized stream; that byte is never written. An exactly capped stream is accepted after confirmed end and a successful digest check when one is required. The aggregate cap includes accepted manifest and record bytes. All seven local release regressions passed again (results/repair_logs/round2_download_regressions_final.json); scientific provenance and generated tables were then refreshed and compared again.


## Release repair round 3, 2026-10-01

The four final verification items are repaired. Public-text hygiene scans the source tree when index metadata is absent or unsupported, pruning ignored and build folders while retaining supported index checks in a checkout. CITATION.cff identifies version 0.1.1 and 2026-10-01; the research context uses the exact primary EMGBench title. The cap description above now matches the accepted/written-byte boundary, including the at-most-one-byte overflow detection read; exact-cap and overflow regressions pass. CI downloads the pilot once through network acceptance, then runs every remaining test against that pilot, with a 15-minute download timeout and a 30-minute combined step deadline. Hosted CI remains unverified.

The complete suite passed 64 tests with no skips or deselections, 95.09% branch-inclusive coverage and 795.705 seconds wall time (results/repair_logs/round3_full_suite.json). Hygiene also passed from a source copy without .git (round3_source_copy.json). Ruff, mypy, pyright and generated-document consistency passed. Fresh evaluation reproduced all 225 scientific point/interval scalars and all other scientific fields exactly; the prediction trace is byte-identical (round3_scientific_comparison.json, 21.788 seconds). Only the four release items and their tests, receipts and this note changed; scientific code, frozen protocol and published result values remain unchanged. The existing process-footprint gate remains UNVERIFIED.
