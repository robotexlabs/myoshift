"""Independent regressions for publication byte, history and scope contracts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest
from scripts import check_wheel
from scripts.generate_documents import limitations_block

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "release_helpers", ROOT / "tests/test_release_repairs.py"
)
assert SPEC is not None and SPEC.loader is not None
HELPERS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPERS)


def git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(  # noqa: S603
        ["/usr/bin/git", *arguments], cwd=root, text=True
    ).strip()


@pytest.fixture
def repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    git(tmp_path, "init", "--initial-branch=main")
    git(tmp_path, "config", "user.name", "Release Tester")
    git(tmp_path, "config", "user.email", "tester@example.invalid")
    (tmp_path / "sample.txt").write_text("public example\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "Initial example")
    monkeypatch.setattr(HELPERS, "ROOT", tmp_path)
    monkeypatch.delenv("MYOSHIFT_AUDIT_REF", raising=False)
    return tmp_path


def test_every_committed_source_digest() -> None:
    data = json.loads((ROOT / "results/results.json").read_text())
    mismatches = [
        name
        for name, digest in data["provenance"]["source_sha256"].items()
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest
    ]
    assert mismatches == [], f"stale source bytes: {mismatches}"


def test_checkout_serialization_policy() -> None:
    attributes = git(ROOT, "check-attr", "eol", "--", "src/myoshift/__init__.py")
    assert attributes.endswith("eol: lf")
    assert b"\r" not in (ROOT / "src/myoshift/__init__.py").read_bytes()


@pytest.mark.parametrize("shape", ["main", "detached", "pull_request"])
def test_history_acceptance_checkout_shapes(repository: Path, shape: str) -> None:
    if shape == "detached":
        git(repository, "checkout", "--detach")
    elif shape == "pull_request":
        git(repository, "checkout", "-b", "contribution")
        (repository / "addition.txt").write_text("reviewed addition\n")
        git(repository, "add", ".")
        git(repository, "commit", "-m", "Add example")
        git(repository, "checkout", "main")
        git(repository, "merge", "--no-ff", "contribution", "-m", "Review merge")
        git(repository, "update-ref", "refs/pull/1/merge", "HEAD")
        git(repository, "checkout", "--detach", "refs/pull/1/merge")
    assert "release" not in git(repository, "branch", "--list").split()
    HELPERS.test_public_commit_metadata_hygiene()


def test_full_author_metadata_is_audited(repository: Path) -> None:
    git(repository, "branch", "release")
    git(repository, "config", "user.name", "co" + "dex")
    git(repository, "commit", "--allow-empty", "-m", "Ordinary change")
    git(repository, "branch", "-f", "release", "HEAD")
    with pytest.raises(AssertionError):
        HELPERS.test_public_commit_metadata_hygiene()


def test_reachable_historical_blobs_are_audited(repository: Path) -> None:
    (repository / "old.log").write_text("co" + "dex\n")
    git(repository, "add", ".")
    git(repository, "commit", "-m", "Historical example")
    git(repository, "rm", "old.log")
    git(repository, "commit", "-m", "Remove example")
    git(repository, "branch", "release")
    with pytest.raises(AssertionError):
        HELPERS.test_public_commit_metadata_hygiene()


def test_png_metadata_is_audited(repository: Path) -> None:
    from PIL import Image, PngImagePlugin

    image = Image.new("RGB", (8, 8))
    image.save(repository / "figure.png")
    git(repository, "add", ".")
    git(repository, "commit", "-m", "Add figure")
    HELPERS.test_public_commit_metadata_hygiene()
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Attribution", "co" + "dex")
    image.save(repository / "figure.png", pnginfo=metadata)
    git(repository, "add", ".")
    git(repository, "commit", "-m", "Change figure metadata")
    with pytest.raises(AssertionError):
        HELPERS.test_public_commit_metadata_hygiene()


def test_shallow_audit_fails_loudly(repository: Path) -> None:
    git(repository, "branch", "release")
    (repository / ".git/shallow").write_text(git(repository, "rev-parse", "HEAD") + "\n")
    with pytest.raises((AssertionError, ValueError), match="shallow"):
        HELPERS.test_public_commit_metadata_hygiene()


def test_explicit_missing_audit_ref_fails(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    git(repository, "branch", "release")
    monkeypatch.setenv("MYOSHIFT_AUDIT_REF", "nonexistent-publication-ref")
    with pytest.raises(subprocess.CalledProcessError):
        HELPERS.test_public_commit_metadata_hygiene()


@pytest.mark.parametrize("relative", ["ordinary.log", "results/repair_logs/receipt.log"])
def test_hygiene_includes_logs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, relative: str
) -> None:
    monkeypatch.setattr(HELPERS, "ROOT", tmp_path)
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("/" + "Users/" + "example/receipt\n")
    assert HELPERS.collect_text_violations([path]) == [relative]


@pytest.mark.parametrize("name", ["co" + "dex", "cla" + "ude", "gpt" + "-6.1"])
def test_hygiene_includes_tool_and_model_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    monkeypatch.setattr(HELPERS, "ROOT", tmp_path)
    path = tmp_path / "receipt.txt"
    path.write_text(name.upper())
    assert HELPERS.collect_text_violations([path]) == ["receipt.txt"]


@pytest.mark.parametrize(
    "filename", ["PUBLICATION_FIX_REPORT_2026-10-01.md", "PUBLICATION_FIX_REPORT_2_2026-10-01.md"]
)
def test_superseded_receipts_label_themselves(filename: str) -> None:
    first = (ROOT / "docs/milestones" / filename).read_text().splitlines()[0]
    assert "Superseded" in first and "historical" in first


def test_licence_manifest_covers_all_public_outputs() -> None:
    notice = (ROOT / "NOTICE").read_text()
    for scope in (
        "docs/ recursively",
        "templates",
        "results/ recursively",
        "historical",
        "repair logs",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "CITATION.cff",
        "https://creativecommons.org/licenses/by/4.0/",
    ):
        assert scope in notice, f"missing licence scope: {scope}"


def test_wheel_helper_uses_ci_distribution_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import zipfile

    monkeypatch.chdir(tmp_path)
    (tmp_path / "dist").mkdir()
    with zipfile.ZipFile(tmp_path / "dist/myoshift-0.1.1-py3-none-any.whl", "w") as wheel:
        for name in ("LICENSE", "NOTICE"):
            wheel.writestr(f"myoshift-0.1.1.dist-info/licenses/{name}", (ROOT / name).read_bytes())
        wheel.writestr(
            "myoshift/protocol/PREREGISTRATION.md", (ROOT / "docs/PREREGISTRATION.md").read_bytes()
        )
    (tmp_path / "LICENSE").write_bytes((ROOT / "LICENSE").read_bytes())
    (tmp_path / "NOTICE").write_bytes((ROOT / "NOTICE").read_bytes())
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/PREREGISTRATION.md").write_bytes(
        (ROOT / "docs/PREREGISTRATION.md").read_bytes()
    )
    monkeypatch.setattr(check_wheel.subprocess, "run", lambda *args, **kwargs: None)
    check_wheel.main()
    assert (tmp_path / "results/repair_logs/wheel_artifact.json").exists()


def test_wheel_install_ignores_external_source_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import zipfile

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PIP_DISABLE_PIP_VERSION_CHECK", "1")
    source = tmp_path / "external-source"
    metadata = source / "myoshift.egg-info"
    metadata.mkdir(parents=True)
    package_metadata = "Metadata-Version: 2.1\nName: myoshift\nVersion: 0.1.1\n"
    (metadata / "PKG-INFO").write_text(package_metadata)
    monkeypatch.setenv("PYTHONPATH", str(source))
    (tmp_path / "dist").mkdir()
    for name in ("LICENSE", "NOTICE", "docs/PREREGISTRATION.md"):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    with zipfile.ZipFile(tmp_path / "dist/myoshift-0.1.1-py3-none-any.whl", "w") as wheel:
        prefix = "myoshift-0.1.1.dist-info/"
        wheel.writestr(prefix + "METADATA", package_metadata)
        wheel.writestr(
            prefix + "WHEEL", "Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
        )
        wheel.writestr(prefix + "RECORD", "")
        for name in ("LICENSE", "NOTICE"):
            wheel.writestr(prefix + "licenses/" + name, (ROOT / name).read_bytes())
        wheel.writestr("myoshift/__init__.py", "")
        wheel.writestr(
            "myoshift/cli.py", "def main(args):\n    assert args == ['verify-scorers']\n"
        )
        wheel.writestr("myoshift/eval/__init__.py", "")
        wheel.writestr(
            "myoshift/eval/benchmark.py",
            "def run_full_benchmark(data_root, output_dir):\n"
            "    return {'runs': [{}]*12, 'provenance': {'protocol_sha256': "
            "'15a1f7dd67a45e8848baa8a88ce6f752b66b46984388064dc037c560b5c04f38'}}\n",
        )
        wheel.writestr(
            "myoshift/protocol/PREREGISTRATION.md", (ROOT / "docs/PREREGISTRATION.md").read_bytes()
        )
    check_wheel.main()
    assert (
        json.loads((tmp_path / "results/repair_logs/wheel_artifact.json").read_text())[
            "isolated_install"
        ]
        == "passed"
    )


def test_evaluator_entry_pages() -> None:
    readme = (ROOT / "README.md").read_text()
    site = (ROOT / "docs/site/index.html").read_text()
    assert len(readme.split()) < 650
    assert "![" in readme and "risk_coverage_person.png" in readme
    assert "<figure>" in site and "<figcaption>" in site
    assert "PUBLICATION_FIX_REPORT_3_2026-10-01.md" in readme
    assert "public-data engineering demonstration" in readme
    assert "Python 3.11" in readme


def test_limits_name_session_calibration_and_do_not_repeat_latency() -> None:
    data = json.loads((ROOT / "results/results.json").read_text())
    text = limitations_block(data)
    assert "participant 44" in text and "lexicographically" in text
    assert "session-3 rest" in text
    assert text.count("feature extraction, acquisition and end-to-end command response") == 1


def test_frozen_protocol_git_and_checkout_bytes() -> None:
    expected = "15a1f7dd67a45e8848baa8a88ce6f752b66b46984388064dc037c560b5c04f38"
    blob = subprocess.check_output(  # noqa: S603
        ["/usr/bin/git", "show", "HEAD:docs/PREREGISTRATION.md"], cwd=ROOT
    )
    assert blob == (ROOT / "docs/PREREGISTRATION.md").read_bytes()
    assert hashlib.sha256(blob).hexdigest() == expected and b"\r\n" in blob


def test_scientific_and_dataset_claim_ceiling_retained() -> None:
    results = (ROOT / "RESULTS.md").read_text()
    notice = (ROOT / "NOTICE").read_text()
    assert "Decoder novelty remains withdrawn" in results
    assert "cannot establish safety equivalence" in results
    assert "rest" in results and "unavailable" in results
    assert "doi:10.13026/ah52-zq51" in notice
    assert "not redistributed" in notice and "CC BY-NC 4.0" in notice
