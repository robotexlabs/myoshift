# Repair amendment 07: unavailable few shot equal budget

Repair-round date label: 2026-10-01, as requested. This is a retrospective amendment, not evidence of prospective registration. Results had already been seen before this change. The frozen preregistration and its hash file are unchanged.

Verification finding: **7**.

What changed and why: Remove the static-LDA fallback. Calibration-only LDA is unavailable when the frozen prefix lacks at least two classes; it has no measured score. Static LDA, bespoke hysteresis and selective LDA use identical source-only labelled training support, with the same independent target calibration budget available to all. Static and hysteresis intentionally do not consume that optional budget. Few-shot by definition has only the calibration data and uses zero source labels. Hysteresis is a fixed reference implementation, not an official or strongest tuned controller.

Reason: the independent verification demonstrated the previous implementation or report did not support its stated evaluation contract. This amendment records the repair after those results, without claiming an evidenced pre-result freeze chronology.
