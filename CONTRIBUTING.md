# Contributing

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks

```bash
ruff check src tests
mypy src
pyright src
pytest
```

## Data

Download the pilot subset with `bash scripts/download_pilot.sh`. Do not commit raw WFDB files.

## Preregistration

Do not edit `docs/PREREGISTRATION.md` after results exist. Use dated amendment files instead.
