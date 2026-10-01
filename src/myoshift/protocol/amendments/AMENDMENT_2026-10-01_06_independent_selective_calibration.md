# Repair amendment 06: independent selective calibration

Repair-round date label: 2026-10-01, as requested. This is a retrospective amendment, not evidence of prospective registration. Results had already been seen before this change. The frozen preregistration and its hash file are unchanged.

Verification finding: **6**.

What changed and why: Fit the selective LDA and its StandardScaler on source windows only; use the independent purged target calibration prefix solely to set an empirical 0.9 quantile of 1 minus maximum class probability. Prediction uses the identical score. Keep fixed margin 0.15 and rest abstention. Remove the affine session normalisation that cancelled inside the refitted scaler. This is empirical confidence rejection with no conformal guarantee and no session adaptation claim. Calibration labels are not used for selective fitting.

Reason: the independent verification demonstrated the previous implementation or report did not support its stated evaluation contract. This amendment records the repair after those results, without claiming an evidenced pre-result freeze chronology.
