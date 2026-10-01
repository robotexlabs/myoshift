# Publication fix report 3, 2026-10-01

**Publication acceptance: BLOCKED on genuine network acquisition.** The repaired
publication candidate exercised all 116 cases using the CI split: 115 passed, one failed because the sandbox
could not resolve the public data host; none skipped. Combined package coverage
is 95.33% (lines 754/782, branches 184/202). A cached run cannot clear this gate.
The hosted Python 3.11/3.12 matrix remains unverified; nothing was pushed.

This round implements the independent second-release review on the fixed `main`
tree. Workspace Git writes were denied (`index.lock: Operation not permitted`),
so the commits are made in a writable temporary clone and exported as
`state/myoshift-main.bundle` and `state/myoshift-release.bundle`. The original
workspace refs remain unchanged. Both author and committer are Amirhossein (Amir)
Daneshpajouh <52765136+Daneshpajouh@users.noreply.github.com>.

## Findings and regressions

The new regressions were first overlaid onto a fresh `b9465df` checkout. Twenty
intentional failures and two passing retention controls were recorded in
`state/round3/regressions-before.xml` and `.log`. The original five report failures
are recorded separately in `baseline-five-failures.log`. A working CRLF checkout
had hidden those five failures; the committed LF checkout exposed them.

| Review item | Repair and before-failing test(s) |
|---|---|
| 1: stale provenance and five failed report cases | LF ordinary-file checkout policy, explicit frozen-byte exceptions, complete source inventory and raw-byte validation. `test_every_committed_source_digest` and `test_checkout_serialization_policy` failed before repair. Existing four report cases and amendment chronology now pass. |
| 2: branch-dependent acceptance | Default audit ref is `HEAD`, with an optional explicit `MYOSHIFT_AUDIT_REF`; missing refs and shallow history fail loudly. `test_history_acceptance_checkout_shapes` failed for default-main, detached and synthetic PR-merge fixtures before repair. CI fetches full history. |
| 3: overstated receipts and hygiene scope | Reports 1 and 2 label themselves superseded at their own tops. `test_superseded_receipts_label_themselves`, `test_full_author_metadata_is_audited`, `test_reachable_historical_blobs_are_audited`, `test_hygiene_includes_logs`, and `test_hygiene_includes_tool_and_model_names` failed before repair. No tracked log or repair-log path is exempted. |
| 4: licence gaps | NOTICE covers root documents, recursive documentation including templates, protocol copies, all results including historical outputs and repair logs, software/configuration and explicit exclusions; CC BY 4.0 URI and upstream credit remain. `test_licence_manifest_covers_all_public_outputs` failed before repair. |
| 5: evaluator entry pages (advisory) | Short public-data engineering case study, embedded annotated operating-point figure, caveat, executable example and compact receipt link. Full tables, limitations and history remain linked. `test_evaluator_entry_pages` failed before repair. |
| 6: supported scientific claims (informational) | Negative result, novelty withdrawal, rest-only calibration, unavailable few-shot fitting, small healthy seated cohort and absence of live/clinical validation remain. The retention control passed before and after; no artificial regression is claimed. |
| 7: dataset route (informational) | GRABMyoFlow and PhysioNet credit, permissive-data attribution and withheld restricted datasets remain. The retention control passed before and after; no new licence investigation or redistribution is claimed. |
| 8: release-only publication boundary | Full selected-history object and metadata audit, including historical blobs and paths; private development history is not exported in the release bundle. Historical-blob/author regressions above failed before repair. Only the release root is eligible for publication auditing. |
| Additional maintenance | Wheel helper now defaults to CI's `dist/`, verifies exact LICENSE/NOTICE and all protocol copies, and can write its receipt externally. `test_wheel_helper_uses_ci_distribution_directory` failed before repair. The additional `test_wheel_install_ignores_external_source_metadata` failed on a round-3 candidate and passed after installer isolation; see `wheel-metadata-before.log` and `wheel-metadata-after.log`. |
| Disclosure detail | Global session calibration explicitly names the first lexicographically ordered 50 windows of participant 44's session-3 rest record; duplicate latency exclusion is removed. `test_limits_name_session_calibration_and_do_not_repeat_latency` failed before repair. |

The additional actual-trace schema regression failed before correcting the nested output/confidence path in the new comparison helper; `trace-schema-before.log` and `trace-schema-after.log` retain that evidence.

Additional controls reject changed source bytes, missing source inventory,
changed protocol/data digests, altered scientific fields or collection order,
and undeclared resource differences. Checkout fixtures preserve frozen protocol
CRLF bytes with `core.autocrlf=true` and `false`. PNG validation and metadata
inspection reject prohibited textual attribution without treating compressed
pixel bytes as words.

## Verification and exact evidence binding

The frozen protocol remains SHA-256
`15a1f7dd67a45e8848baa8a88ce6f752b66b46984388064dc037c560b5c04f38`, in both its
Git blob and checkout, with the packaged copy equal. All 70 recorded source
inputs and 192 waveform/header digests are validated against raw bytes and the
complete expected path inventories. Generated outputs were rebuilt from a
clean committed source checkout after final serialization. All 490 scientific
numerical fields remain exactly equal to the previous artifact; the intentional
source-binding updates are recorded separately from resource timing differences.

Verification uses Python 3.11.15 on macOS arm64 and the existing dependency
toolchain, with imports explicitly bound to the clean clone's `src/`. This is a
clean-clone check, not a claim of a fresh dependency download. The separately
verified public cache is declared input, not a successful fresh acquisition.
The wheel is installed in a new environment using declared existing dependency
packages, imported from that environment, and exercised away from source.

| Gate | Local observation / exact command |
|---|---|
| Complete suite | `python -m pytest -o addopts= -m network` plus the available-suite command below; 115 passed, 1 network failure, no skips (network and non-network commands run separately) |
| Available suite | `python -m pytest -o addopts= -m 'not network' --cov=myoshift --cov-fail-under=90`; final clean-clone receipt records the exit and counts |
| Source/data/history binding | `python scripts/verify_publication.py --ref HEAD --output EXTERNAL_RECEIPT`; zero hygiene hits, 70 source and 192 data digests |
| Static checks | `ruff check .`, `mypy src`, `pyright src`; clean (20 source files; no type errors or warnings) |
| Document consistency | `python scripts/generate_documents.py --check`; passes before regeneration |
| Headless regeneration | `python scripts/run_benchmark.py`; completes from a clean checkout, with `MPLBACKEND=Agg` |
| Repeatability | Two isolated release checkouts; `python scripts/compare_regeneration.py FIRST SECOND --output EXTERNAL_COMPARISON` |
| Wheel | `python -m build --wheel --no-isolation`; `python scripts/check_wheel.py --dist-dir dist --dependency-site DEPENDENCY_SITE --output EXTERNAL_WHEEL_RECEIPT` |
| Text/model hygiene | `git grep -I -n -i -E PATTERN HEAD --`; zero textual hits (grep exit 1). PNG metadata and the full release object graph are audited separately. |
| Fresh network gate | Empty isolated destination; real `test_clean_download_smoke` fails on DNS before acquisition, with zero downloaded records |
| Release topology | One exported release ref, one parentless commit, exact human author/committer, release tree equal to fixed main tree |

Runtime, RSS and per-run predict p50/p95 timings are the only JSON-pointer
allowlist in `scripts/compare_regeneration.py`. Source/data hashes, all other
provenance, scientific fields, configurations, ordering and inventories must
match exactly. Documentation normalization is limited to the corresponding
result digest, resource sentence and final predict-latency table cells. Figures
must be byte-identical. Trace confidence alone permits an absolute difference
of at most 1e-12 with identical rounding to six decimals; every other trace field
and row count must match. This tolerance is not a scientific-value allowance.

Final IDs cannot be embedded in a file within their own tree without a circular
hash. The external companion `state/round3/FINAL_RECEIPT.json` binds the final main
and release OIDs, common tree, both bundle hashes, exact commands and exit states,
environment, before/after status, all tracked file hashes, source/data provenance,
and hashes of the raw logs. It is produced after final commits from a new clone
of the release bundle. `state/round3/final-input-binding.json`, suite XML/coverage,
regeneration comparison, environment snapshot and wheel receipt are companions.
These external records establish the exact tested tree; earlier retained logs
remain historical observations, not current commit-bound acceptance evidence.

## Remaining boundary

Publication remains blocked until the genuine empty-cache acquisition test and
the configured hosted matrix have direct green receipts. Local fixes, coverage,
static checks, digest verification and cached regeneration do not establish
network delivery or hosted acceptance. The compressed/swapped memory gate,
threshold frontier, matched-recall comparison, prospective preregistration,
external dataset, live operation and clinical utility remain unverified or
untested as stated in the scientific reports. No new validation experiment,
client-delivery claim, deployment, submission or push occurred.
