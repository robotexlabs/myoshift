# Repair amendment 04: purge and reset

Repair-round date label: 2026-10-01, as requested. This is a retrospective amendment, not evidence of prospective registration. Results had already been seen before this change. The frozen preregistration and its hash file are unchanged.

Verification finding: **4**.

What changed and why: Keep the frozen first-window calibration prefix, then purge every test window sharing raw sample support with any calibration window in the same independent record. Unknown raw support excludes the entire calibration record. Decoder state resets at every independent record boundary; filename order makes no claim about continuous acquisition order.

Reason: the independent verification demonstrated the previous implementation or report did not support its stated evaluation contract. This amendment records the repair after those results, without claiming an evidenced pre-result freeze chronology.
