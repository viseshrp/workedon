import re

from click.testing import CliRunner
import pytest

from workedon import __version__, cli, exceptions


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


def test_empty_fetch():
    result = CliRunner().invoke(cli.what)
    assert result.exit_code == 0
    assert "Nothing to show" in result.output


@pytest.mark.parametrize(
    "work",
    [
        (["painting the garage"]),
        (["studying for the SAT", "@ 3pm friday"]),
        (["pissing my wife off", "@ 2:30pm yesterday"]),
        (["writing some tests", "@ 9 hours ago"]),
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
        (["recording a demo"], ["--id"]),
        (["recording a demo"], ["-i"]),
    ],
)
def test_save_and_fetch_id(work, option):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # fetch
    matches = re.search(r".*id: ([0-9a-f]{40}).*", result.output)
    work_id = matches.group(1)
    option.append(work_id)
    result = CliRunner().invoke(cli.what, option)
    verify_work_output(result, work)


@pytest.mark.parametrize(
    "work, option",
    [
        (["calling 911"], ["-n", "1"]),
        (["weights at the gym"], ["--count", "1"]),
        (["yard work at home", "@ 3pm friday"], ["--on", "friday"]),
        (["learning guitar", "@ 9pm friday"], ["--at", "9pm friday"]),
        (
            ["gaining Indian Independence", "@ 1pm August 15 1947"],
            ["--since", "1947", "-r", "-n", "1"],
        ),
        (["framing a photo", "@ 1:34pm yesterday"], ["--yesterday"]),
        (["taking pictures", "@ 12:34pm yesterday"], ["-e"]),
        (["training for a 4k", "@ 1 hour 3 mins ago"], ["--today"]),
        (["training for a 10k", "@ 59 mins ago"], ["-o"]),
        (["setting up my homelab", "@ 1 hour ago "], ["--past-day"]),
        (["setting up my garden", "@ 2 hours ago "], ["-d"]),
        (
            ["setting up my garage", "@ 2pm 6 days ago "],
            ["--past-week", "-r", "-n", "1"],
        ),
        (
            ["setting up my kitchen", "@ 1pm 6 days ago "],
            ["-w", "-r", "-n", "1"],
        ),
        (
            ["cleaning my car", "@ 2pm 27 days ago "],
            ["--past-month", "-r", "-n", "1"],
        ),
        (
            ["vacuuming my car", "@ 1pm 27 days ago "],
            ["-m", "-r", "-n", "1"],
        ),
        (
            ["learning to make sushi", "@ 2pm 360 days ago "],
            ["--past-year", "-r", "-n", "1"],
        ),
        (
            ["learning to brew soy sauce", "@ 1pm 360 days ago "],
            ["-y", "-r", "-n", "1"],
        ),
        (
            ["learning to drive", "@ 3pm June 3rd 2020"],
            ["--from", "June 2nd 2020", "--to", "June 4th 2020"],
        ),
        (["learning to cook", "@ 3pm yesterday"], ["-f", "2 days ago", "-t", "3:05pm yesterday"]),
        (["watching tv", "@ 9am"], ["-g"]),
        (["taking wife shopping", "@ 3pm"], ["--no-page"]),
    ],
)
def test_save_and_fetch_others(work, option):
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
    "work, option_del, option_what",
    [
        (
            ["watching Modern Family", "@ 8:53pm"],
            ["--at", "8:53pm", "--delete"],
            ["--at", "8:53pm"],
        ),
    ],
)
def test_save_and_fetch_delete(work, option_del, option_what):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # fetch and delete
    result = CliRunner().invoke(cli.what, option_del, input="y")
    assert result.exit_code == 0
    assert "deleted successfully" in result.output
    # check
    result = CliRunner().invoke(cli.what, option_what)
    assert result.exit_code == 0
    assert "Nothing to show" in result.output


@pytest.mark.parametrize(
    "option",
    [
        (["--at", "4:44pm 5 years ago", "--delete"]),
    ],
)
def test_save_and_fetch_delete_empty(option):
    # fetch
    result = CliRunner().invoke(cli.what, option)
    assert result.exit_code == 0
    assert "Nothing to delete" in result.output


@pytest.mark.parametrize(
    "work, option",
    [
        (["vacuuming", "@ 2am"], ["-l"]),
        (["eating", "@ 3am"], ["--text-only"]),
    ],
)
def test_save_and_fetch_textonly(work, option):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # fetch
    result = CliRunner().invoke(cli.what, option)
    assert result.exit_code == 0
    assert f"* {work[0]}" in result.output
    assert "id:" not in result.output
    assert "Date:" not in result.output


# db
@pytest.mark.parametrize(
    "options",
    [
        (["--print-path"]),
    ],
)
def test_db_print_path(options):
    result = CliRunner().invoke(cli.db, options)
    assert result.exit_code == 0
    assert result.output.startswith("The database is located at: ")


@pytest.mark.parametrize(
    "options",
    [
        (["--vacuum"]),
    ],
)
def test_db_vacuum(options):
    result = CliRunner().invoke(cli.db, options)
    assert result.exit_code == 0
    assert result.output.startswith("VACUUM complete.")


@pytest.mark.parametrize(
    "work, option_db, option_what",
    [
        (["watching Lost"], ["--truncate"], ["--last"]),
    ],
)
def test_db_truncate(work, option_db, option_what):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # trunc
    result = CliRunner().invoke(cli.db, option_db, input="y")
    assert result.exit_code == 0
    assert "Deletion successful." in result.output
    # check
    result = CliRunner().invoke(cli.what, option_what)
    assert result.exit_code == 0
    assert "Nothing to show" in result.output


@pytest.mark.parametrize(
    "options",
    [
        (["--version"]),
    ],
)
def test_db_version(options):
    result = CliRunner().invoke(cli.db, options)
    assert result.exit_code == 0
    assert result.output.startswith("SQLite version: ")


# exceptions
@pytest.mark.parametrize(
    "work",
    [
        ([" ", "@ 9pm 8 days ago"]),
    ],
)
def test_save_and_fetch_invalid(work):
    # save
    result = CliRunner().invoke(cli.main, work)
    assert result.exit_code == 1
    assert not result.output.startswith("Work saved.")
    assert exceptions.InvalidWorkError.detail in result.output


@pytest.mark.parametrize(
    "work",
    [
        (["Creating the world", "@ lolololol"]),
    ],
)
def test_save_and_fetch_date_invalid(work):
    # save
    result = CliRunner().invoke(cli.main, work)
    assert result.exit_code == 1
    assert not result.output.startswith("Work saved.")
    assert exceptions.InvalidDateTimeError.detail in result.output


@pytest.mark.parametrize(
    "work",
    [
        (["Walking the dog", "@ 5pm tomorrow"]),
    ],
)
def test_save_and_fetch_date_in_future(work):
    # save
    result = CliRunner().invoke(cli.main, work)
    assert result.exit_code == 1
    assert not result.output.startswith("Work saved.")
    assert exceptions.DateTimeInFutureError.detail in result.output


@pytest.mark.parametrize(
    "work, option",
    [
        (["doing my taxes", "@ 9pm 8 days ago"], ["-t", "3pm yesterday"]),
    ],
)
def test_save_and_fetch_start_absent(work, option):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # fetch
    result = CliRunner().invoke(cli.what, option)
    assert result.exit_code == 1
    assert work[0] not in result.output
    assert exceptions.StartDateAbsentError.detail in result.output


@pytest.mark.parametrize(
    "work, option",
    [
        (["making pasta", "@ 9pm 5 days ago"], ["-f", "3pm yesterday", "-t", "3pm 5 days ago"]),
    ],
)
def test_save_and_fetch_start_greater(work, option):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # fetch
    result = CliRunner().invoke(cli.what, option)
    assert result.exit_code == 1
    assert work[0] not in result.output
    assert exceptions.StartDateGreaterError.detail in result.output


@pytest.mark.parametrize(
    "work, option",
    [
        (["cardio at the gym", "@ 5:53pm tuesday"], ["--count", "0"]),
    ],
)
def test_save_and_fetch_zero_count(work, option):
    # save
    result = CliRunner().invoke(cli.main, work)
    verify_work_output(result, work)
    assert result.output.startswith("Work saved.")
    # fetch
    result = CliRunner().invoke(cli.what, option)
    assert result.exit_code == 1
    assert work[0] not in result.output
    assert exceptions.CannotFetchWorkError.detail in result.output
