# Redactions

On 2026-10-12 the host name field was removed from results/results.json for privacy. No measured value changed. The documents were regenerated with the unchanged generator, which prints unknown when the field is absent.

On 2026-10-18 the benchmark was rerun because the README generator changed and results/results.json binds its digest. The host name field was removed again in the same way, and the documents were regenerated. Every science field compared (768 in all) and the prediction traces match the 2026-10-12 file exactly. Runtime, memory, latency and Python patch version are new receipts from this run.

Later on 2026-10-18 the benchmark was rerun again because the CI workflow changed and results/results.json binds the digest of .github/workflows/ci.yml. The host name field was removed in the same way and the documents were regenerated. The 490 numeric fields outside the resource allowlist of scripts/compare_regeneration.py, the per-file data digests, the prediction traces and both figures match the earlier 2026-10-18 file exactly. Runtime, memory and latency are new receipts from this run.
