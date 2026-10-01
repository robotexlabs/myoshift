# Retrospective protocol serialization amendment, 2026-10-01

Results had already been seen before this amendment. The frozen preregistration text and its intended SHA-256 `15a1f7dd67a45e8848baa8a88ce6f752b66b46984388064dc037c560b5c04f38` remain unchanged.

Git checkout without explicit attributes normalised the protocol to LF (3,057 bytes, hash `52bfa03bc3d6c5da10a54f29ad4b1fb99408c30144ce1ef07820b9f416eb2c3d`). The preserved frozen bytes use CRLF line endings (3,133 bytes). `.gitattributes` now pins CRLF for the protocol copies in `docs/` and `src/myoshift/protocol/`.

This amendment records the correction retrospectively. It does not claim prospective freeze chronology. Rebuild wheels and regenerate provenance from a clean checkout after this change.
