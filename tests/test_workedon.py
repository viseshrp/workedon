#!/usr/bin/env python

"""Tests for `workedon` package."""

from click.testing import CliRunner
import pytest

from workedon import __main__


@pytest.fixture
def runner():
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_cli_main(runner):
    """Test the CLI."""
    result = runner.invoke(__main__.main)
    assert result.exit_code == 0
    help_result = runner.invoke(__main__.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
