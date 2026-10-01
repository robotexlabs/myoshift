# Repair amendment 08: verified wrist ring channels

Repair-round date label: 2026-10-01, as requested. This is a retrospective amendment, not evidence of prospective registration. Results had already been seen before this change. The frozen preregistration and its hash file are unchanged.

Verification finding: **8**.

What changed and why: Select channel names W1-W12 exactly once each, in that order. For the official extension layout they correspond to zero-based indices 1-6 and 9-14. Form two six-channel rings W1-W6 and W7-W12, and permute each separately by +2 for the proxy electrode condition. Missing or duplicate wrist names fail. Twelve channels produce 36 features. The permutation is a geometry-motivated proxy, not measured physical displacement. Source: PhysioNet GRABMyoFlow 1.0.0 official converter grabmyoflow_wfdb_to_mat_static.py, EXTENSION_INDICES_KEEP; https://physionet.org/content/grabmyo-flow/1.0.0/.

Reason: the independent verification demonstrated the previous implementation or report did not support its stated evaluation contract. This amendment records the repair after those results, without claiming an evidenced pre-result freeze chronology.
