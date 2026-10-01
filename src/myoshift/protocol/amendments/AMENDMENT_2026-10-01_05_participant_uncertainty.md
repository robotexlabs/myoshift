# Repair amendment 05: participant uncertainty

Repair-round date label: 2026-10-01, as requested. This is a retrospective amendment, not evidence of prospective registration. Results had already been seen before this change. The frozen preregistration and its hash file are unchanged.

Verification finding: **5**.

What changed and why: Replace the single participant-47 person and electrode evaluation with leave-one-participant-out folds over all four available participants. Session 3 remains held out. Aggregate out-of-fold predictions and bootstrap complete participant clusters with paired method draws (500 resamples, seed 42). Intervals are descriptive small-pilot participant intervals with shared training folds, not population safety guarantees. Single-participant API requests are labelled conditional. Threshold-swept risk-coverage and matched-recall comparisons remain explicitly untested; figures show operating points only. Zero-count intervals do not establish safety equivalence.

Reason: the independent verification demonstrated the previous implementation or report did not support its stated evaluation contract. This amendment records the repair after those results, without claiming an evidenced pre-result freeze chronology.
