"""CLI tests."""

from click.testing import CliRunner

from myoshift.cli import main


def test_verify_scorers() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["verify-scorers"])
    assert result.exit_code == 0
    assert "passed" in result.output
