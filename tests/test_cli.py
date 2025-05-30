from __future__ import annotations

from datetime import datetime
import re

from click.testing import CliRunner, Result
import pytest

from workedon import __version__, cli, exceptions
from workedon.conf import CONF_PATH


def verify_work_output(result: Result, work: str) -> None:
    assert result.exit_code == 0
    assert work in result.output
    assert "id:" in result.output
    assert "Date:" in result.output


@pytest.mark.parametrize(
    "options",
    [
        (["-h"]),
        (["--help"]),
        (["what", "-h"]),
        (["what", "--help"]),
    ],
)
def test_help(options: list[str]) -> None:
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
def test_version(options: list[str]) -> None:
    result = CliRunner().invoke(cli.main, options)
    assert result.exit_code == 0
    assert __version__ in result.output


def test_empty_fetch() -> None:
    result = CliRunner().invoke(cli.what)
    assert result.exit_code == 0
    assert "Nothing to show" in result.output


@pytest.mark.parametrize(
    "work",
    [
        [
            ("washing the car", ""),
            ("studying for the SAT", " @ 3pm friday"),
            ("pissing my wife off", " @ 2:30pm yesterday"),
        ],
        [
            ("writing some tests", " @ 9 hours ago"),
            ("finding a friend", " @ 2pm 4 days ago"),
        ],
    ],
)
def test_save_and_fetch(work: list[tuple[str, str]]) -> None:
    for description, suffix in work:
        cmd = f"{description}{suffix}"
        result = CliRunner().invoke(cli.main, cmd)
        verify_work_output(result, description)
        assert result.output.startswith("Work saved.")

        result = CliRunner().invoke(cli.what, ["--no-page", "--since", "2 weeks ago"])
        verify_work_output(result, description)


@pytest.mark.parametrize(
    "work, option, valid",
    [
        (("building workedon", ""), ["-s"], True),
        (("studying for the GRE", ""), ["--last"], True),
        (("talking to my brother", " @ 3pm 3 years ago"), ["--last"], False),
    ],
)
def test_save_and_fetch_last(work: tuple[str, str], option: list[str], valid: bool) -> None:
    description, suffix = work
    result = CliRunner().invoke(cli.main, f"{description}{suffix}")
    verify_work_output(result, description)
    assert result.output.startswith("Work saved.")

    result = CliRunner().invoke(cli.what, ["--no-page", *option])
    if valid:
        verify_work_output(result, description)
    else:
        assert result.exit_code == 0
        assert description not in result.output


@pytest.mark.parametrize(
    "work, option",
    [
        (("recording a demo", ""), ["--id"]),
        (("recording a demo", ""), ["-i"]),
    ],
)
def test_save_and_fetch_id(work: tuple[str, str], option: list[str]) -> None:
    description, suffix = work
    result = CliRunner().invoke(cli.main, f"{description}{suffix}")
    verify_work_output(result, description)
    assert result.output.startswith("Work saved.")

    match = re.search(r"id:\s+([0-9a-f]{32})", result.output)
    assert match, "No id found in save output"
    work_id = match.group(1)

    result = CliRunner().invoke(cli.what, [*option, work_id])
    verify_work_output(result, description)


@pytest.mark.parametrize(
    "opt, env",
    [
        ("", "WORKEDON_DATETIME_FORMAT"),
        ("--datetime-format", ""),
    ],
)
def test_save_and_fetch_date_opt_env(opt: str, env: str, monkeypatch: pytest.MonkeyPatch) -> None:
    result = CliRunner().invoke(cli.main, ["testing date opt"])
    assert result.output.startswith("Work saved.")

    strp_string = "%a %b %d"
    if env:
        monkeypatch.setenv(env, strp_string)
    opts: list[str] = []
    if opt:
        opts = [opt, strp_string]

    result = CliRunner().invoke(cli.what, ["--no-page", *opts])
    match = re.search(r"Date:\s+(.*)\n", result.output)
    assert match, "Date line not found"
    date_text = match.group(1)
    date_object = datetime.strptime(date_text, strp_string)
    assert date_object.year != datetime.now().year


@pytest.mark.parametrize(
    "opt, env",
    [
        ("", "WORKEDON_TIME_ZONE"),
        ("--time-zone", ""),
    ],
)
def test_save_and_fetch_timezone_opt_env(
    opt: str, env: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = CliRunner().invoke(cli.main, ["testing timezone opt"])
    assert result.output.startswith("Work saved.")

    tz = "Asia/Tokyo"
    if env:
        monkeypatch.setenv(env, tz)
    opts: list[str] = []
    if opt:
        opts = [opt, tz]

    result = CliRunner().invoke(cli.what, ["--no-page", *opts])
    assert "+0900" in result.output or "JST" in result.output


@pytest.mark.parametrize(
    "work, option",
    [
        (("calling 911", ""), ["-n", "1"]),
        (("weights at the gym", ""), ["--count", "1"]),
        (("yard work at home", " @ 3pm friday"), ["--on", "friday"]),
        (("learning guitar", " @ 9pm friday"), ["--at", "9pm friday"]),
        (
            ("gaining Indian Independence", " @ 1pm August 15 1947"),
            ["--since", "1947", "-r", "-n", "1"],
        ),
        (("framing a photo", " @ 1:34pm yesterday"), ["--yesterday"]),
        (("taking pictures", " @ 12:34pm yesterday"), ["-e"]),
        (("training for a 4k", ""), ["--today"]),
        (("training for a 10k", ""), ["-o"]),
        (("setting up my homelab", " @ 1 hour ago "), ["--past-day"]),
        (("setting up my garden", " @ 2 hours ago "), ["-d"]),
        (
            ("setting up my garage", " @ 2pm 6 days ago "),
            ["--past-week", "-r", "-n", "1"],
        ),
        (("setting up my kitchen", " @ 1pm 6 days ago "), ["-w", "-r", "-n", "1"]),
        (
            ("cleaning my car", " @ 2pm 27 days ago "),
            ["--past-month", "-r", "-n", "1"],
        ),
        (("vacuuming my car", " @ 1pm 27 days ago "), ["-m", "-r", "-n", "1"]),
        (
            ("learning to make sushi", " @ 2pm 360 days ago "),
            ["--past-year", "-r", "-n", "1"],
        ),
        (("learning to brew soy sauce", " @ 1pm 360 days ago "), ["-y", "-r", "-n", "1"]),
        (
            ("learning to drive", " @ 3pm June 3rd 2020"),
            ["--from", "June 2nd 2020", "--to", "June 4th 2020"],
        ),
        (
            ("learning to cook", " @ 3pm yesterday"),
            ["-f", "2 days ago", "-t", "3:05pm yesterday"],
        ),
        (("watching tv", " @ 9am"), []),
        (("taking wife shopping", " @ 3pm"), []),
    ],
)
def test_save_and_fetch_others(work: tuple[str, str], option: list[str]) -> None:
    description, suffix = work
    result = CliRunner().invoke(cli.main, f"{description}{suffix}")
    verify_work_output(result, description)
    assert result.output.startswith("Work saved.")

    result = CliRunner().invoke(cli.what, ["--no-page", *option])
    verify_work_output(result, description)


@pytest.mark.parametrize(
    "work, option",
    [
        (["building a house", "destroying the house"], ["-r", "-n", "1"]),
        (["home improvement", "home destruction"], ["--reverse", "-n", "1"]),
    ],
)
def test_save_and_fetch_reverse(work: list[str], option: list[str]) -> None:
    # save
    for w in work:
        result = CliRunner().invoke(cli.main, w)
        verify_work_output(result, w)
        assert result.output.startswith("Work saved.")
    # fetch reversed
    result = CliRunner().invoke(cli.what, ["--no-page", *option])
    assert result.exit_code == 0
    assert work[1] not in result.output


@pytest.mark.parametrize(
    "work, option_del, option_what",
    [
        (
            ("watching Modern Family", " @ 8:53am"),
            ["--at", "8:53am", "--delete"],
            ["--at", "8:53am"],
        ),
    ],
)
def test_save_and_fetch_delete(
    work: tuple[str, str], option_del: list[str], option_what: list[str]
) -> None:
    description, suffix = work
    result = CliRunner().invoke(cli.main, f"{description}{suffix}")
    verify_work_output(result, description)
    assert result.output.startswith("Work saved.")

    result = CliRunner().invoke(cli.what, ["--no-page", *option_del], input="y")
    assert result.exit_code == 0
    assert "deleted successfully" in result.output

    result = CliRunner().invoke(cli.what, ["--no-page", *option_what])
    assert result.exit_code == 0
    assert "Nothing to show" in result.output


@pytest.mark.parametrize(
    "option",
    [
        (["--at", "4:44pm 5 years ago", "--delete"]),
    ],
)
def test_save_and_fetch_delete_empty(option: list[str]) -> None:
    result = CliRunner().invoke(cli.what, ["--no-page", *option])
    assert result.exit_code == 0
    assert "Nothing to delete" in result.output


@pytest.mark.parametrize(
    "work, option",
    [
        (("vacuuming", " @ 2am"), ["-l"]),
        (("eating", " @ 3am"), ["--text-only"]),
    ],
)
def test_save_and_fetch_textonly(work: tuple[str, str], option: list[str]) -> None:
    description, suffix = work
    result = CliRunner().invoke(cli.main, f"{description}{suffix}")
    verify_work_output(result, description)
    assert result.output.startswith("Work saved.")

    result = CliRunner().invoke(cli.what, ["--no-page", *option])
    assert result.exit_code == 0
    assert f"* {description}" in result.output
    assert "id:" not in result.output
    assert "Date:" not in result.output


# db operations
@pytest.mark.parametrize(
    "options",
    [
        (["--print-db-path"]),
    ],
)
def test_db_print_path(options: list[str]) -> None:
    result = CliRunner().invoke(cli.main, options)
    assert result.exit_code == 0
    assert "won.db" in result.output


@pytest.mark.parametrize(
    "options",
    [
        (["--vacuum-db"]),
    ],
)
def test_db_vacuum(options: list[str]) -> None:
    result = CliRunner().invoke(cli.main, options)
    assert result.exit_code == 0
    assert "VACUUM complete." in result.output


@pytest.mark.parametrize(
    "work, option_db, option_what",
    [
        (("watching Lost", ""), ["--truncate-db"], ["--last"]),
    ],
)
def test_db_truncate(work: tuple[str, str], option_db: list[str], option_what: list[str]) -> None:
    description, suffix = work
    result = CliRunner().invoke(cli.main, f"{description}{suffix}")
    verify_work_output(result, description)
    assert result.output.startswith("Work saved.")

    result = CliRunner().invoke(cli.main, option_db, input="y")
    assert result.exit_code == 0
    assert "Deletion successful." in result.output

    result = CliRunner().invoke(cli.what, ["--no-page", *option_what])
    assert result.exit_code == 0
    assert "Nothing to show" in result.output


@pytest.mark.parametrize(
    "options",
    [
        (["--db-version"]),
    ],
)
def test_db_version(options: list[str]) -> None:
    result = CliRunner().invoke(cli.main, options)
    assert result.exit_code == 0
    assert result.output.startswith("SQLite version: ")


# config dumping
@pytest.mark.parametrize(
    "options",
    [
        (["--print-settings-path"]),
    ],
)
def test_conf_print_path(options: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    with capsys.disabled():
        result = CliRunner().invoke(cli.main, options)
        assert result.exit_code == 0
        assert "wonfile.py" in result.output


@pytest.mark.parametrize(
    "options",
    [
        (["--print-settings"]),
    ],
)
def test_conf_print_settings(options: list[str]) -> None:
    with CONF_PATH.open("a") as f:
        f.write('TIME_FORMAT = "%H:%M %z"\n')
    result = CliRunner().invoke(cli.main, options)
    assert result.exit_code == 0
    assert 'TIME_FORMAT="%H:%M %z"' in result.output


# exception cases
@pytest.mark.parametrize(
    "work",
    [
        (" ", " @ 9pm 8 days ago"),
    ],
)
def test_save_and_fetch_invalid(work: tuple[str, str]) -> None:
    description, suffix = work
    result = CliRunner().invoke(cli.main, f"{description}{suffix}")
    assert result.exit_code == 1
    assert exceptions.InvalidWorkError.detail in result.output


@pytest.mark.parametrize(
    "work",
    [
        ("Creating the world", " @ lolololol"),
    ],
)
def test_save_and_fetch_date_invalid(work: tuple[str, str]) -> None:
    description, suffix = work
    result = CliRunner().invoke(cli.main, f"{description}{suffix}")
    assert result.exit_code == 1
    assert exceptions.InvalidDateTimeError.detail in result.output


@pytest.mark.parametrize(
    "work",
    [
        ("Walking the dog", " @ 5pm tomorrow"),
    ],
)
def test_save_and_fetch_date_in_future(work: tuple[str, str]) -> None:
    description, suffix = work
    result = CliRunner().invoke(cli.main, f"{description}{suffix}")
    assert result.exit_code == 1
    assert exceptions.DateTimeInFutureError.detail in result.output


@pytest.mark.parametrize(
    "work, option",
    [
        (("doing my taxes", " @ 9pm 8 days ago"), ["-t", "3pm yesterday"]),
    ],
)
def test_save_and_fetch_start_absent(work: tuple[str, str], option: list[str]) -> None:
    description, suffix = work
    result = CliRunner().invoke(cli.main, f"{description}{suffix}")
    verify_work_output(result, description)
    assert result.output.startswith("Work saved.")

    result = CliRunner().invoke(cli.what, ["--no-page", *option])
    assert result.exit_code == 1
    assert description not in result.output
    assert exceptions.StartDateAbsentError.detail in result.output


@pytest.mark.parametrize(
    "work, option",
    [
        (("making pasta", " @ 9pm 5 days ago"), ["-f", "3pm yesterday", "-t", "3pm 5 days ago"]),
    ],
)
def test_save_and_fetch_start_greater(work: tuple[str, str], option: list[str]) -> None:
    description, suffix = work
    result = CliRunner().invoke(cli.main, f"{description}{suffix}")
    verify_work_output(result, description)
    assert result.output.startswith("Work saved.")

    result = CliRunner().invoke(cli.what, ["--no-page", *option])
    assert result.exit_code == 1
    assert description not in result.output
    assert exceptions.StartDateGreaterError.detail in result.output


@pytest.mark.parametrize(
    "work, option",
    [
        (("cardio at the gym", " @ 5:53pm tuesday"), ["--count", "0"]),
    ],
)
def test_save_and_fetch_zero_count(work: tuple[str, str], option: list[str]) -> None:
    description, suffix = work
    result = CliRunner().invoke(cli.main, f"{description}{suffix}")
    verify_work_output(result, description)
    assert result.output.startswith("Work saved.")

    result = CliRunner().invoke(cli.what, ["--no-page", *option])
    assert result.exit_code == 1
    assert description not in result.output
    assert exceptions.CannotFetchWorkError.detail in result.output
