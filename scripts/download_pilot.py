"""Bounded, checksum-verified retrieval of the fixed public pilot."""

from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
import time
import urllib.request
from pathlib import Path

UPSTREAM = "https://physionet.org/files/grabmyo-flow/1.0.0/"
MAX_BYTES = 64 * 1024 * 1024
MAX_FILE_BYTES = 4 * 1024 * 1024
TIMEOUT = 120


def fetch(url: str, target: Path, expected: str | None, limit: int) -> int:
    """Never replace a target until a bounded transfer and digest check succeed."""
    if not url.startswith(UPSTREAM):
        raise ValueError("unexpected download URL")
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=target.name + ".", suffix=".part", dir=target.parent)
    temporary = Path(name)
    size = 0
    digest = hashlib.sha256()
    deadline = time.monotonic() + TIMEOUT
    try:
        with (
            os.fdopen(descriptor, "wb") as output,
            urllib.request.urlopen(url, timeout=10) as response,  # noqa: S310
        ):
            if int(response.headers.get("Content-Length", "0")) > limit:
                raise ValueError("download exceeds byte cap")
            while True:
                if time.monotonic() > deadline:
                    raise TimeoutError("download deadline exceeded")
                chunk = response.read(min(65536, limit - size + 1))
                if not chunk:
                    break
                size += len(chunk)
                if size > limit:
                    raise ValueError("download exceeds byte cap")
                digest.update(chunk)
                output.write(chunk)
        if expected is not None and digest.hexdigest() != expected:
            raise ValueError("checksum mismatch")
        temporary.replace(target)
        return size
    finally:
        temporary.unlink(missing_ok=True)


def download(root: Path) -> None:
    manifest = root / "SHA256SUMS.txt"
    total = fetch(UPSTREAM + "SHA256SUMS.txt", manifest, None, min(MAX_FILE_BYTES, MAX_BYTES))
    expected = {}
    for line in manifest.read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        expected[name.lstrip("*").removeprefix("./")] = digest
    for participant in (44, 45, 46, 47):
        for session in (1, 2, 3):
            for gesture in (1, 2, 3, 17):
                for trial in (1, 2):
                    name = (
                        f"session{session}_participant{participant}_gesture{gesture}_trial{trial}"
                    )
                    for extension in ("hea", "dat"):
                        relative = (
                            f"static_extension_WFDB/session{session}/"
                            f"session{session}_participant{participant}/{name}.{extension}"
                        )
                        total += fetch(
                            UPSTREAM + relative,
                            root / relative,
                            expected[relative],
                            min(MAX_FILE_BYTES, MAX_BYTES - total),
                        )
    print(f"Verified 96 records; {total} transferred bytes including manifest")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data/raw/grabmyo-flow",
    )
    download(parser.parse_args().destination)
