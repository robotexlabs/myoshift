# Data manifest

## Primary: GRABMyoFlow 1.0.0

- **Source:** https://physionet.org/content/grabmyo-flow/1.0.0/
- **Licence:** Creative Commons Attribution 4.0 International (verified from `LICENSE.txt`)
- **Attribution:** Ehlert, Tung, Pradhan; PhysioNet 2026; doi:10.13026/ah52-zq51
- **Platform citation:** Pollard et al., Nature Health 2026; doi:10.1038/s44360-026-00096-z

### Pilot subset (this repository evaluation)

| Field | Value |
|-------|-------|
| Participants | 44, 45, 46, 47 |
| Sessions | 1, 2, 3 |
| Gestures | 1, 2, 3, 17 (rest) |
| Trials per gesture | 1, 2 |
| Downloaded size | ~30 MB (96 WFDB records) |
| Path | `data/raw/grabmyo-flow/static_extension_WFDB/` |

### Download command

```bash
mkdir -p data/raw/grabmyo-flow
# See scripts/download_pilot.sh
```

Full dataset is 4.3 GB ZIP; not required for reproduction of published pilot results.

## Excluded datasets

| Dataset | Reason |
|---------|--------|
| NinaPro DB6 | No explicit file licence on official site |
| Meta generic neuromotor interface | CC BY-NC 4.0 on the inspected official repository release; an earlier manuscript referenced CC BY-NC-SA (non-commercial) |
| Hyser PR | Deferred (37 GB; licence ODC-By permits use but exceeds pilot budget) |
