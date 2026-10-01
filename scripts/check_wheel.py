"""Build artifact installation into a fresh environment, away from source imports."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def verify_contents(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        for filename in ("LICENSE", "NOTICE"):
            matches = [
                name for name in archive.namelist() if name.endswith("/licenses/" + filename)
            ]
            if len(matches) != 1 or archive.read(matches[0]) != Path(filename).read_bytes():
                raise ValueError("wheel licence content mismatch: " + filename)
        for path in [Path("docs/PREREGISTRATION.md"), *Path("docs/amendments").glob("*.md")]:
            packaged = "myoshift/protocol/" + path.relative_to("docs").as_posix()
            if archive.read(packaged) != path.read_bytes():
                raise ValueError("wheel protocol content mismatch: " + str(path))


def main(
    dist_dir: Path = Path("dist"),
    dependency_site: Path | None = None,
    receipt: Path = Path("results/repair_logs/wheel_artifact.json"),
) -> None:
    wheels = sorted(dist_dir.glob("myoshift-*.whl"))
    if len(wheels) != 1:
        raise ValueError("expected exactly one built wheel")
    wheel = wheels[0].resolve()
    verify_contents(wheel)
    data_root = Path("data/raw/grabmyo-flow/static_extension_WFDB").resolve()
    with tempfile.TemporaryDirectory(prefix="myoshift-wheel-") as directory:
        environment = Path(directory) / "venv"
        subprocess.run(  # noqa: S603
            [sys.executable, "-m", "venv", str(environment)], timeout=180, check=True
        )
        if dependency_site is not None:
            site = next((environment / "lib").glob("python*/site-packages"))
            (site / "verified-dependencies.pth").write_text(str(dependency_site.resolve()) + "\n")
        install = [
            str(environment / "bin/python"),
            "-I",
            "-m",
            "pip",
            "install",
            "--ignore-installed",
        ]
        if dependency_site is not None:
            install.append("--no-deps")
        commands = [
            [*install, str(wheel)],
            [
                str(environment / "bin/python"),
                "-I",
                "-c",
                "import sys,myoshift; from pathlib import Path; "
                "assert Path(myoshift.__file__).is_relative_to(sys.prefix); "
                "print(sys.version); print('installed wheel import verified'); "
                'from myoshift.cli import main; main(["verify-scorers"])',
            ],
        ]
        commands.append(
            [
                str(environment / "bin/python"),
                "-I",
                "-c",
                "from pathlib import Path; from myoshift.eval.benchmark import run_full_benchmark; "
                f"r=run_full_benchmark(Path({str(data_root)!r}), Path('output')); "
                "assert len(r['runs']) == 12; "
                "assert r['provenance']['protocol_sha256'] == "
                "'15a1f7dd67a45e8848baa8a88ce6f752b66b46984388064dc037c560b5c04f38'",
            ]
        )
        for command in commands:
            print(json.dumps(command), flush=True)
            subprocess.run(command, cwd=directory, timeout=180, check=True)  # noqa: S603
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(
        json.dumps(
            {
                "wheel": str(wheels[0]),
                "sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
                "isolated_install": "passed",
                "dependency_source": "existing site" if dependency_site else "package resolver",
                "licence_and_protocol_contents": "verified byte-identical",
                "python": sys.version,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"))
    parser.add_argument("--dependency-site", type=Path)
    parser.add_argument(
        "--output", type=Path, default=Path("results/repair_logs/wheel_artifact.json")
    )
    args = parser.parse_args()
    main(args.dist_dir, args.dependency_site, args.output)
