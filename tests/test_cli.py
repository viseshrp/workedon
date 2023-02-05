from click.testing import CliRunner
import pytest

from workedon import __version__, cli


def verify_work_output(result, work):
    assert result.exit_code == 0
    assert work[0] in result.output
    assert "id:" in result.output
    assert "Date:" in result.output


@pytest.mark.parametrize(
    "options",
    [
        ([]),
        (["-h"]),
        (["--help"]),
        (["what", "-h"]),
        (["what", "--help"]),
    ],
)
def test_help(options):
    result = CliRunner().invoke(cli.main, options)
    assert result.exit_code == 0
    assert result.output.startswith("Usage: ")
    assert "-h, --help" in result.output


@pytest.mark.parametrize(
    "options",
    [
        (["-v"]),
        (["--version"]),
    ],
)
def test_version(options):
    result = CliRunner().invoke(cli.main, options)
    assert result.exit_code == 0
    assert __version__ in result.output


@pytest.mark.parametrize(
    "work",
    [
        (["painting the garage"]),
        (["studying for the SAT", "@ 3pm friday"]),
        (["pissing my wife off", "@ 2:30pm yesterday"]),
        (["writing some tests", "@ 2 days ago"]),
        (["finding a friend", "@ 2pm 4 days ago"]),
    ],
)
def test_save_and_fetch(work):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # fetch
    result = CliRunner().invoke(cli.what)
    verify_work_output(result, work)


@pytest.mark.parametrize(
    "work, option, valid",
    [
        (["building workedon"], ["-s"], True),
        (["studying for the GRE"], ["--last"], True),
        (["talking to my brother", "@ 3pm 3 years ago"], ["--last"], False),
    ],
)
def test_save_and_fetch_last(work, option, valid):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # fetch
    result = CliRunner().invoke(cli.what, option)
    if valid:
        verify_work_output(result, work)
    else:
        assert result.exit_code == 0
        assert work[0] not in result.output


@pytest.mark.parametrize(
    "work, option",
    [
        (["calling 911"], ["-n", "1"]),
        (["weights at the gym"], ["--count", "1"]),
    ],
)
def test_save_and_fetch_count(work, option):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # fetch
    result = CliRunner().invoke(cli.what, option)
    verify_work_output(result, work)


@pytest.mark.parametrize(
    "work, option",
    [
        (["building a house"], ["-r", "-n", "1"]),
        (["home improvement"], ["--reverse", "-n", "1"]),
    ],
)
def test_save_and_fetch_reverse(work, option):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # fetch
    result = CliRunner().invoke(cli.what, option)
    assert result.exit_code == 0
    assert work[0] not in result.output


@pytest.mark.parametrize(
    "work, option",
    [
        (["building a house"], ["--delete"]),
    ],
)
def test_save_and_fetch_delete(work, option):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # fetch
    result = CliRunner().invoke(cli.what, option)
    assert result.exit_code == 0
    assert work[0] not in result.output


@pytest.mark.parametrize(
    "work, option",
    [
        (["yard work at home", "@ 3pm friday"], ["--on", "friday"]),
    ],
)
def test_save_and_fetch_on(work, option):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # fetch
    result = CliRunner().invoke(cli.what, option)
    verify_work_output(result, work)


@pytest.mark.parametrize(
    "work, option",
    [
        (["learning guitar", "@ 3pm friday"], ["--at", "3pm friday"]),
    ],
)
def test_save_and_fetch_at(work, option):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # fetch
    result = CliRunner().invoke(cli.what, option)
    verify_work_output(result, work)
