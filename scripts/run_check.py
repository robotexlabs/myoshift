"""Run a foreground command with a bounded timeout and resource receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import resource
import subprocess
import sys
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    directory = Path("results/repair_logs")
    directory.mkdir(parents=True, exist_ok=True)

    def snapshot() -> dict[str, str]:
        return {
            str(p): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [
                *Path("src").rglob("*.py"),
                *Path("scripts").glob("*.py"),
                *Path("tests").glob("*.py"),
                Path("pyrightconfig.json"),
                Path("pyproject.toml"),
                Path("docs/PREREGISTRATION.md"),
                Path("docs/PREREGISTRATION.sha256"),
            ]
        }

    before = snapshot()
    start = time.monotonic()
    measurements = []
    with (directory / f"{args.name}.log").open("w") as log:
        command = args.command
        if command[:1] == ["--"]:
            command = command[1:]
        log.write(f"Command: {command!r}\n")
        log.flush()
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)  # noqa: S603
        timed_out = False
        try:
            while process.poll() is None:
                if time.monotonic() - start > args.timeout:
                    timed_out = True
                    process.kill()
                    break
                if not measurements or time.monotonic() - measurements[-1]["elapsed_s"] - start > 5:
                    try:
                        receipt = subprocess.run(  # noqa: S603 - fixed top argv
                            [
                                "/usr/bin/top",
                                "-l",
                                "1",
                                "-pid",
                                str(process.pid),
                                "-stats",
                                "pid,mem",
                            ],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            check=False,
                        )
                        measurements.append(
                            {
                                "elapsed_s": time.monotonic() - start,
                                "exit": receipt.returncode,
                                "stdout": receipt.stdout,
                                "stderr": receipt.stderr,
                            }
                        )
                    except OSError as exc:
                        measurements.append(
                            {"elapsed_s": time.monotonic() - start, "error": str(exc)}
                        )
                time.sleep(0.1)
        finally:
            process.wait()
        elapsed = time.monotonic() - start
        log.write(f"\nExit: {process.returncode}\nRuntime seconds: {elapsed:.6f}\n")
    child_rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    peak_child_rss_mb = child_rss / (1024 * 1024) if sys.platform == "darwin" else child_rss / 1024
    after = snapshot()
    changed = [p for p in before.keys() | after.keys() if before.get(p) != after.get(p)]
    receipt = {
        "source_changed_during_run": changed,
        "child_peak_rss_mb": peak_child_rss_mb,
        "source_sha256": before,
        "name": args.name,
        "argv": command,
        "exit": process.returncode,
        "timeout_s": args.timeout,
        "timed_out": timed_out,
        "runtime_s": elapsed,
        "top": measurements,
    }
    (directory / f"{args.name}.json").write_text(json.dumps(receipt, indent=2))
    print(
        f"{args.name}: exit {process.returncode}, {elapsed:.3f}s, log {directory}/{args.name}.log"
    )
    raise SystemExit(process.returncode or (1 if changed else 0))


if __name__ == "__main__":
    main()
