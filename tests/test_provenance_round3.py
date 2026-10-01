"""Full byte inventory acceptance and deliberate tampering controls."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from myoshift.provenance import hashes, source_files, verify

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def inputs(tmp_path: Path) -> tuple[Path, dict]:
    data = json.loads((ROOT / "results/results.json").read_text())
    for path in [*source_files(ROOT), ROOT / "docs/PREREGISTRATION.md"]:
        target = tmp_path / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    return tmp_path, data


def test_all_source_and_data_digests() -> None:
    data = json.loads((ROOT / "results/results.json").read_text())
    verified = verify(ROOT, data, ROOT / "data/raw/grabmyo-flow/static_extension_WFDB")
    assert verified["source_digests"] == len(source_files(ROOT))
    assert verified["data_digests"] == 192


@pytest.mark.parametrize("failure", ["source_bytes", "source_inventory", "protocol"])
def test_tampered_source_is_rejected(inputs: tuple[Path, dict], failure: str) -> None:
    root, data = inputs
    if failure == "source_bytes":
        path = root / "src/myoshift/__init__.py"
        path.write_bytes(path.read_bytes() + b"\n")
    elif failure == "source_inventory":
        data["provenance"]["source_sha256"].pop(next(iter(data["provenance"]["source_sha256"])))
    else:
        path = root / "docs/PREREGISTRATION.md"
        path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="mismatch"):
        verify(root, data)


@pytest.mark.parametrize("failure", ["digest", "inventory"])
def test_tampered_data_is_rejected(inputs: tuple[Path, dict], failure: str) -> None:
    root, data = inputs
    raw = ROOT / "data/raw/grabmyo-flow/static_extension_WFDB"
    if failure == "digest":
        data["provenance"]["data_sha256"][next(iter(data["provenance"]["data_sha256"]))] = "0" * 64
    else:
        data["config"]["n_records"] += 1
    with pytest.raises(ValueError, match="mismatch"):
        verify(root, data, raw)


def test_installed_package_provenance_inventory(tmp_path: Path) -> None:
    (tmp_path / "example.py").write_text("# installed module\n")
    (tmp_path / "protocol").mkdir()
    (tmp_path / "protocol/PREREGISTRATION.md").write_text("frozen example\n")
    paths = source_files(tmp_path)
    assert [path.relative_to(tmp_path).as_posix() for path in paths] == [
        "example.py",
        "protocol/PREREGISTRATION.md",
    ]
    assert len(hashes(tmp_path, paths)) == 2


@pytest.mark.parametrize("autocrlf", ["true", "false"])
def test_checkout_byte_contract_across_git_settings(tmp_path: Path, autocrlf: str) -> None:
    origin = tmp_path / "origin"
    origin.mkdir()
    subprocess.run(["/usr/bin/git", "init", str(origin)], check=True, capture_output=True)  # noqa: S603
    (origin / ".gitattributes").write_bytes((ROOT / ".gitattributes").read_bytes())
    (origin / "ordinary.py").write_bytes(b"# ordinary LF\n")
    (origin / "docs").mkdir()
    (origin / "docs/PREREGISTRATION.md").write_bytes(
        (ROOT / "docs/PREREGISTRATION.md").read_bytes()
    )
    for args in (
        ["add", "."],
        [
            "-c",
            "user.name=Release Tester",
            "-c",
            "user.email=tester@example.invalid",
            "commit",
            "-m",
            "Byte contract example",
        ],
    ):
        subprocess.run(["/usr/bin/git", *args], cwd=origin, check=True, capture_output=True)  # noqa: S603
    clone = tmp_path / "clone"
    subprocess.run(  # noqa: S603
        [
            "/usr/bin/git",
            "clone",
            "--no-hardlinks",
            "--config",
            "core.autocrlf=" + autocrlf,
            str(origin),
            str(clone),
        ],
        check=True,
        capture_output=True,
    )
    assert (clone / "ordinary.py").read_bytes() == b"# ordinary LF\n"
    assert (clone / "docs/PREREGISTRATION.md").read_bytes() == (
        ROOT / "docs/PREREGISTRATION.md"
    ).read_bytes()
