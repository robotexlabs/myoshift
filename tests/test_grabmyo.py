"""GRABMyo loader tests."""

from pathlib import Path

import pytest

from myoshift.data.grabmyo import discover_trials, parse_record_name


def test_parse_record_name() -> None:
    parsed = parse_record_name("session1_participant44_gesture3_trial2.hea")
    assert parsed == (1, 44, 3, 2)


def test_discover_trials_on_downloaded_subset() -> None:
    root = Path("data/raw/grabmyo-flow/static_extension_WFDB")
    if not root.exists():
        pytest.skip("downloaded data not present")
    trials = discover_trials(root)
    assert len(trials) > 0
    assert trials[0].n_channels == 16
