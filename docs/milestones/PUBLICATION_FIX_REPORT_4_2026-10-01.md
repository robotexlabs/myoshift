# Publication fix report 4, 2026-10-01

The two required publication defects in the final independent review of
`a2b02939c340f4c074370f7d7af6c11af63df7e4` are resolved. The review stays local
and is excluded from the public tree. No push or publication occurred.

## Required fixes

1. All 27 captured machine-specific path occurrences in the ten reviewed logs
   were replaced with neutral temporary-location placeholders. Each published
   log now starts with an explicit redacted-copy notice. Original bytes are
   preserved outside the public release in `state/round4/original_logs/`.
   The external `state/round4/redaction_manifest.json` records original and
   redacted SHA-256 digests, each substitution and occurrence counts. Only path
   text and the notice changed; recorded successes, failures, numbers and
   historical observations remain intact.
2. The historical `repair_report_final` command row in
   `docs/milestones/REPAIR_2026-10-01_REPORT.md` now matches its named immutable
   JSON receipt: runtime 0.10666649999984656 seconds, displayed as **0.107**,
   and child peak RSS **20.53125 MiB**. Its argv, exit, evidence link and all
   appended repair history are retained. The historical report generator was
   not run, and the receipt was not edited.

The redacted inventory is `results/repair_logs/` followed by:
`corrected_evaluation.log`, `regressions_before.log`,
`regressions_before_validated.log`, `round2_full_suite.log`,
`round2_install.log`, `round2_wheel_install.log`, `wheel_install.log`,
`wheel_install_documented.log`, `wheel_install_release.log` and
`wheel_install_verified.log`.

## Regression and verification evidence

The publication audit now rejects home-directory paths, private local-root
paths and macOS temporary-folder paths, including historical blobs removed
from later trees. A new regression reads every tracked file as raw bytes,
without log, binary, configuration or self exclusions. The existing path
fixture was rewritten using split strings so it cannot bypass its own policy.
Additional tests exercise removed historical paths, actual omitted prefixes,
redaction notices and the historical command row's argv, exit, runtime and RSS.
Before repair these tests recorded **7 failures and 2 passing controls**;
after repair all **9 passed**. Both observations are preserved externally.

| Check | Result / command |
|---|---|
| Complete available suite, including slow cases | 124 passed, one network case deselected, no skips; `python -m pytest -o addopts= -m 'not network' --cov=myoshift --cov-fail-under=90` |
| Coverage | 95.33% combined; 754/782 statements and 184/202 branches |
| Static checks | `ruff check .`, `mypy src`, `pyright src`; clean |
| Generated documents | `python scripts/generate_documents.py --check`; clean |
| Source/data/history audit | `python scripts/verify_publication.py --ref HEAD --output EXTERNAL_RECEIPT`; 71 source digests, 192 data digests, zero hygiene violations |
| Regeneration | `MPLBACKEND=Agg python scripts/run_benchmark.py`; source bindings refreshed through the existing pipeline |
| Scientific retention | 490 non-resource numerical fields equal to the predecessor, all 80,499 trace rows equal with zero confidence differences, both current figures byte-identical |
| Repeat regeneration | `python scripts/compare_regeneration.py FIRST SECOND --output EXTERNAL_COMPARISON`; only the existing explicit resource-field allowance |
| Wheel | `python -m build --wheel --no-isolation`; isolated install and benchmark through `scripts/check_wheel.py`, exact licence and protocol copies |
| Release topology | One parentless release-r4 commit; tree identical to fixed main; exact requested human author and committer |

Only three source bindings changed: the audit, the existing fixture and the new
regression file. Generated reports were refreshed from the final source bytes.
Protocol bytes, upstream data bindings and all scientific values are preserved.
Timing, cumulative RSS and per-run predict latency remain execution measurements.
Five generated documents match the predecessor after the existing named
result-digest and resource-value normalization. The comparison records source
binding changes separately and does not allow arbitrary provenance differences.

Checks use Python 3.11.15 and the existing local dependency toolchain, with clone
imports explicitly verified. The 192-file digest-verified public cache is an
input to local replay. Installation and wheel checks do not claim fresh
dependency downloads. Final commands, exit states, coverage, tracked-file hashes,
object counts, identities, commit/tree IDs and bundle hashes are bound externally
in `state/round4/FINAL_RECEIPT.json` and its companion logs and JSON receipts.
Self-referential final commit IDs are not embedded in this report.

## Release construction and gate binding

Workspace Git staging was denied with `index.lock: Operation not permitted`.
As in round 3, a writable temporary clone preserves main's development ancestry
and adds the fixes on main. A new parentless release commit is built from exactly
that main tree, as branch `release-r4`. Both refs are exported in
`state/myoshift-fix4.bundle`; workspace refs remain unchanged. A separate
`state/myoshift-release-r4.bundle` exports only release-r4 for public-history
review. The combined fix bundle contains private development history and must
not be used as the public publication history. Original logs and local review
material are excluded from both tracked trees.

Author and committer are Amirhossein (Amir) Daneshpajouh
<52765136+Daneshpajouh@users.noreply.github.com>.

The final independent review accepted genuine network acquisition and hosted
Python 3.11/3.12 execution for **a2b0293**. Those receipts remain bound to that
predecessor OID. They are not relabelled as execution of release-r4, and the
historical failed network log is not converted into a pass. No new network
acquisition or hosted run was performed in this round. The final release-r4
commit/tree is locally checked as recorded in the external companion receipt.
The existing scientific, live-operation, clinical and footprint limitations
remain unchanged. No push occurred.
