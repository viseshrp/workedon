from click.testing import CliRunner
import pytest

from workedon import __main__


@pytest.mark.parametrize(
    "options",
    (
        ["-h"],
        ["--help"],
        ["what", "-h"],
        ["what", "--help"],
    ),
)
def test_help(options):
    result = CliRunner().invoke(__main__.main, options)
    assert result.exit_code == 0
    assert result.output.startswith("Usage: ")
    assert "-h, --help" in result.output


@pytest.mark.parametrize(
    "options",
    (
        ["painting the garage"],
        ["studying for the SAT @ June 2010"],
        ["studying for the SAT @ 2:30pm yesterday"],
        ["studying for the SAT @ 2 days ago"],
        ["studying for the SAT @ 2pm 2 days ago"],
    ),
)
def test_save(options):
    result = CliRunner().invoke(__main__.main, options)
    assert result.exit_code == 0
    assert result.output.startswith("Work saved.")
    assert "id:" in result.output
    assert "Date:" in result.output
