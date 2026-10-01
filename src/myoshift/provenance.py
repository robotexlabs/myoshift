"""Hash raw publication inputs and reject incomplete or stale bindings."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def source_files(root: Path) -> list[Path]:
    """Generated outputs are excluded to avoid a self-referential hash cycle."""
    if (root / "pyproject.toml").is_file():
        paths = [
            *(root / "src").rglob("*.py"),
            *(root / "scripts").glob("*.py"),
            *(root / "tests").glob("*.py"),
            *(root / "docs/amendments").glob("*.md"),
            *(root / ".github/workflows").glob("*.yml"),
            *[
                root / name
                for name in (
                    "pyproject.toml",
                    "pyrightconfig.json",
                    ".gitattributes",
                    "LICENSE",
                    "NOTICE",
                    "CITATION.cff",
                    "docs/negative-result-report.md.in",
                )
            ],
        ]
    else:
        paths = [*root.rglob("*.py"), *(root / "protocol").rglob("*.md")]
    return sorted(paths)


def hashes(root: Path, paths: list[Path]) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(paths)
    }


def verify(root: Path, data: dict[str, Any], data_root: Path | None = None) -> dict[str, int]:
    """Check every recorded digest and the complete expected path inventory."""
    provenance = data["provenance"]
    expected_sources = provenance["source_sha256"]
    if expected_sources != hashes(root, source_files(root)):
        raise ValueError("source provenance mismatch: regenerate from final checkout bytes")
    protocol = root / "docs/PREREGISTRATION.md"
    if hashlib.sha256(protocol.read_bytes()).hexdigest() != provenance["protocol_sha256"]:
        raise ValueError("protocol hash mismatch")
    data_count = 0
    if data_root is not None:
        paths = [p for p in data_root.rglob("*") if p.suffix in (".dat", ".hea")]
        actual = hashes(data_root, paths)
        if actual != provenance["data_sha256"]:
            raise ValueError("data provenance mismatch")
        if len(actual) != 2 * data["config"]["n_records"]:
            raise ValueError("data record inventory mismatch")
        data_count = len(actual)
    return {"source_digests": len(expected_sources), "data_digests": data_count}
