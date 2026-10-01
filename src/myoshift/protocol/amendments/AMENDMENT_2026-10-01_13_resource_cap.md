# Retrospective resource amendment, 2026-10-01

Results had already been seen before this amendment. The frozen preregistration and its SHA-256 remain unchanged.

The governing build cap is 8 GB per process across feature extraction, fitting, evaluation and document generation. This stricter cap supersedes the frozen protocol's 12 GB stop for subsequent execution. Neither cap is deleted from the historical record.

The required measurement is peak process footprint, including compressed and swapped memory, as reported by macOS top MEM. The library's default 2,048 MiB cumulative peak RSS check after each fold is a separate measurement and does not cover initial feature extraction continuously. Small observed RSS values cannot certify either footprint cap.

Footprint compliance remains UNVERIFIED for all phases. No appropriate peak footprint receipt is available. This amendment reconciles the rules retrospectively and makes no prospective registration or resource-certification claim. Stop a run if a measured process footprint exceeds 8 GB; obtain a suitable receipt before declaring this gate passed.
