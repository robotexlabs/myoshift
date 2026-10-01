# Repair amendment 02: command events exposure

Repair-round date label: 2026-10-01, as requested. This is a retrospective amendment, not evidence of prospective registration. Results had already been seen before this change. The frozen preregistration and its hash file are unchanged.

Verification finding: **2**.

What changed and why: An emitted command is a non-abstained non-rest decision with confidence at least 0.5. Dwell is one actual decision interval (one window); onset is the first such decision or a change of command. Offset is rest, abstention, confidence below 0.5, a command change or an independent record boundary. There is no additional refractory interval. Holding a command counts once until offset. Each eligible non-rest trial is one metadata-defined gesture event, detected if a matching command occurs in its test portion. These are trial events, not physiological onsets. Rest exposure is the union of eligible decision intervals from window-end to the next window-end, with the last interval clipped at the raw record end. The 200 ms initial feature warm-up and calibration/purged intervals are excluded. Actual quantised stride is 81/2048 s at defaults, not 0.04 s. Unavailable exposure and wholly abstained risk are null. Legacy test fixtures without duration may infer decision duration from within-record timestamps, but single-window exposure is unavailable. Window recall is retained separately for comparison with the withdrawn scorer.

Reason: the independent verification demonstrated the previous implementation or report did not support its stated evaluation contract. This amendment records the repair after those results, without claiming an evidenced pre-result freeze chronology.
