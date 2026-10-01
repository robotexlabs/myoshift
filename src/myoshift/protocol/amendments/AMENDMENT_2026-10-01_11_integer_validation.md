# Repair amendment 11: integer validation

Repair-round date label: 2026-10-01, as requested. This is a retrospective amendment, not evidence of prospective registration. Results had already been seen before this change. The frozen preregistration and its hash file are unchanged.

Verification finding: **13**.

What changed and why: Reject non-positive window/stride/sample-rate inputs and negative calibration budgets at CLI and library boundaries. Enforce the existing measured RSS and inference-latency budgets; report RSS as cumulative process high-water mark, not isolated run footprint. top footprint measurement is blocked by the execution sandbox, and remains unverified. Downloader timeout, byte-limit and manifest acceptance changes in the rest of finding 13 are outside this packet.

Reason: the independent verification demonstrated the previous implementation or report did not support its stated evaluation contract. This amendment records the repair after those results, without claiming an evidenced pre-result freeze chronology.
