# Repair amendment 03: ratio aggregation

Repair-round date label: 2026-10-01, as requested. This is a retrospective amendment, not evidence of prospective registration. Results had already been seen before this change. The frozen preregistration and its hash file are unchanged.

Verification finding: **3**.

What changed and why: Production metrics sum sufficient statistics across complete resampled clusters before taking ratios. Recall uses only eligible gesture events (and window recall only gesture windows); false-rate uses only measured rest exposure; risk uses only accepted windows. Undefined ratios are null and omitted from interval quantiles. Perfect and empty systems are tested through the production bootstrap.

Reason: the independent verification demonstrated the previous implementation or report did not support its stated evaluation contract. This amendment records the repair after those results, without claiming an evidenced pre-result freeze chronology.
