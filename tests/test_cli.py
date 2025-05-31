from __future__ import annotations

from datetime import datetime
import re

from click.testing import CliRunner, Result
import pytest

from workedon import __version__, cli, exceptions
from workedon.conf import CONF_PATH


def verify_work_output(result: Result, description: str) -> None:
    assert result.exit_code == 0, result.output
    assert description in result.output
    assert "id:" in result.output
    assert "Date:" in result.output


def save_and_verify(runner: CliRunner, command: str, description: str) -> None:
    result = runner.invoke(cli.main, command)
    verify_work_output(result, description)
    assert result.output.startswith("Work saved.")


@pytest.mark.parametrize(
    "options",
    [
        ["-h"],
        ["--help"],
        ["what", "-h"],
        ["what", "--help"],
    ],
)
def test_help(runner: CliRunner, options: list[str]) -> None:
    result = runner.invoke(cli.main, options)
    assert result.exit_code == 0
    assert result.output.startswith("Usage: ")
    assert "-h, --help" in result.output


@pytest.mark.parametrize(
    "options",
    [
        ["-v"],
        ["--version"],
    ],
)
def test_version(runner: CliRunner, options: list[str]) -> None:
    result = runner.invoke(cli.main, options)
    assert result.exit_code == 0
    assert __version__ in result.output


def test_empty_fetch(runner: CliRunner) -> None:
    result = runner.invoke(cli.what)
    assert result.exit_code == 0
    assert "Nothing to show" in result.output


# -- Basic save & fetch scenarios ------------------------------------------------


@pytest.mark.parametrize(
    "command, description",
    [
        ("washing the car", "washing the car"),
        ("studying for the SAT @ 3pm friday", "studying for the SAT"),
        ("pissing my wife off @ 2:30pm yesterday", "pissing my wife off"),
        ("writing tests @ 9 hours ago", "writing tests"),
    ],
)
def test_save_and_fetch(runner: CliRunner, command: str, description: str) -> None:
    save_and_verify(runner, command, description)

    # Fetch recently saved work
    result = runner.invoke(cli.what, ["--no-page", "--since", "2 weeks ago"])
    verify_work_output(result, description)


# -- Fetch last entry ------------------------------------------------------------


@pytest.mark.parametrize(
    "command, description, valid",
    [
        ("building workedon", "building workedon", True),
        ("studying for the GRE", "studying for the GRE", True),
        ("talking to my brother @ 3pm 3 years ago", "talking to my brother", False),
    ],
)
def test_fetch_last(runner: CliRunner, command: str, description: str, valid: bool) -> None:
    save_and_verify(runner, command, description)

    result = runner.invoke(cli.what, ["--no-page", "--last"])
    if valid:
        verify_work_output(result, description)
    else:
        assert result.exit_code == 0
        assert description not in result.output


# -- Fetch by ID ----------------------------------------------------------------


def test_fetch_by_id(runner: CliRunner) -> None:
    description = "recording a demo"
    save_and_verify(runner, description, description)

    # extract ID
    save_result = runner.invoke(cli.main, description).output
    match = re.search(r"id:\s+([0-9a-f]{32})", save_result)
    assert match, "ID not found"
    work_id = match.group(1)

    fetch_result = runner.invoke(cli.what, ["--no-page", "--id", work_id])
    verify_work_output(fetch_result, description)


# -- Format & timezone options ---------------------------------------------------


@pytest.mark.parametrize(
    "opt, env, fmt",
    [
        ([], "WORKEDON_DATETIME_FORMAT", "%a %b %d"),
        (["--datetime-format", "%a %b %d"], "", "%a %b %d"),
    ],
)
def test_datetime_format_option(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    opt: list[str],
    env: str,
    fmt: str,
) -> None:
    description = "testing date opt"

    # Save and make sure the output was written
    save = runner.invoke(cli.main, description.split())
    assert save.exit_code == 0
    assert "Work saved." in save.output

    # If we're using the env-var variant, set it
    if env:
        monkeypatch.setenv(env, fmt)

    # Fetch with no paging, passing either --datetime-format or nothing
    args = ["--no-page", *opt]
    result = runner.invoke(cli.what, args)
    assert result.exit_code == 0

    # Grab the Date line and parse it with the format we expect
    m = re.search(r"Date:\s+(.*)\n", result.output)
    assert m, result.output
    datetime.strptime(m.group(1), fmt)


@pytest.mark.parametrize(
    "opt, env",
    [
        ([], "WORKEDON_TIME_ZONE"),
        (["--time-zone", "Asia/Tokyo"], ""),
    ],
)
def test_timezone_option(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, opt: list[str], env: str
) -> None:
    description = "testing timezone opt"
    save_and_verify(runner, description, description)

    if env:
        monkeypatch.setenv(env, "Asia/Tokyo")
    result = runner.invoke(cli.what, ["--no-page", *opt])
    assert "+0900" in result.output or "JST" in result.output


# -- Other fetch filters ---------------------------------------------------------


@pytest.mark.parametrize(
    "command, flag",
    [
        ("calling 911", ["--count", "1"]),  # 18
        ("weights at the gym", ["--count", "1"]),  # 19
        ("yard work at home @ 3pm friday", ["--on", "friday"]),  # 20
        ("learning guitar @ 9pm friday", ["--at", "9pm friday"]),  # 21
        (
            "gaining Indian Independence @ 1pm August 15 1947",
            ["--since", "1947", "-r", "-n", "1"],
        ),  # 22
        ("framing a photo @ 1:34pm yesterday", ["--yesterday"]),  # 23
        ("taking pictures @ 12:34pm yesterday", ["-e"]),  # 24
        ("training for a 4k", ["--today"]),  # 25
        ("training for a 10k", ["-o"]),  # 26
        ("setting up my homelab @ 1 hour ago", ["--past-day"]),  # 27
        ("setting up my garden @ 2 hours ago", ["-d"]),  # 28
        ("setting up my garage @ 2pm 6 days ago", ["--past-week", "-r", "-n", "1"]),  # 29
        ("setting up my kitchen @ 1pm 6 days ago", ["-w", "-r", "-n", "1"]),  # 30
        ("cleaning my car @ 2pm 27 days ago", ["--past-month", "-r", "-n", "1"]),  # 31
        ("vacuuming my car @ 1pm 27 days ago", ["-m", "-r", "-n", "1"]),  # 32
        ("learning to make sushi @ 2pm 360 days ago", ["--past-year", "-r", "-n", "1"]),  # 33
        ("learning to brew soy sauce @ 1pm 360 days ago", ["-y", "-r", "-n", "1"]),  # 34
        (
            "learning to drive @ 3pm June 3rd 2020",
            ["--from", "June 2nd 2020", "--to", "June 4th 2020"],
        ),  # 35
        ("learning to cook @ 3pm yesterday", ["-f", "2 days ago", "-t", "3:05pm yesterday"]),  # 36
        ("watching tv @ 9am", ["-g"]),  # 37
        ("taking wife shopping @ 3pm", ["--no-page"]),  # 38
        (
            "weights at the gym",
            ["--count", "1"],
        ),  # (duplicate “weights at the gym” if you want to test both)
    ],
)
def test_save_and_fetch_others(runner: CliRunner, command: str, flag: list[str]) -> None:
    description = command.split(" @")[0]
    save_and_verify(runner, command, description)

    result = runner.invoke(cli.what, ["--no-page", *flag])
    verify_work_output(result, description)


# -- Deletion --------------------------------------------------------------------


def test_delete_work(runner: CliRunner) -> None:
    description = "watching Modern Family"
    timestamp = "@ 8:53am"
    save_and_verify(runner, f"{description} {timestamp}", description)

    # delete
    result = runner.invoke(cli.what, ["--no-page", "--at", "8:53am", "--delete"], input="y")
    assert result.exit_code == 0
    assert "deleted successfully" in result.output

    # nothing left
    result = runner.invoke(cli.what, ["--no-page", "--at", "8:53am"])
    assert "Nothing to show" in result.output


def test_delete_empty(runner: CliRunner) -> None:
    result = runner.invoke(cli.what, ["--no-page", "--delete", "--at", "4:44pm 5 years ago"])
    assert result.exit_code == 0
    assert "Nothing to delete" in result.output


# -- Text-only output -----------------------------------------------------------


@pytest.mark.parametrize("flag", [["-l"], ["--text-only"]])
def test_text_only(runner: CliRunner, flag: list[str]) -> None:
    description = "vacuuming"
    save_and_verify(runner, f"{description} @ 2am", description)

    result = runner.invoke(cli.what, ["--no-page", *flag])
    assert result.exit_code == 0
    assert f"* {description}" in result.output
    assert "id:" not in result.output
    assert "Date:" not in result.output


# -- Database maintenance -------------------------------------------------------


@pytest.mark.parametrize("options", [["--print-db-path"]])
def test_db_print_path(runner: CliRunner, options: list[str]) -> None:
    result = runner.invoke(cli.main, options)
    assert result.exit_code == 0
    assert "won.db" in result.output


@pytest.mark.parametrize("options", [["--vacuum-db"]])
def test_db_vacuum(runner: CliRunner, options: list[str]) -> None:
    result = runner.invoke(cli.main, options)
    assert result.exit_code == 0
    assert "VACUUM complete." in result.output


@pytest.mark.parametrize("options", [["--db-version"]])
def test_db_version(runner: CliRunner, options: list[str]) -> None:
    result = runner.invoke(cli.main, options)
    assert result.exit_code == 0
    assert result.output.startswith("SQLite version:")


@pytest.mark.parametrize("options", [["--print-settings-path"]])
def test_conf_print_path(
    runner: CliRunner, capsys: pytest.CaptureFixture[str], options: list[str]
) -> None:
    with capsys.disabled():
        result = runner.invoke(cli.main, options)
        assert result.exit_code == 0
        assert "wonfile.py" in result.output


@pytest.mark.parametrize("options", [["--print-settings"]])
def test_conf_print_settings(runner: CliRunner, options: list[str]) -> None:
    with CONF_PATH.open("a") as f:
        f.write('TIME_FORMAT = "%H:%M %z"\n')
    result = runner.invoke(cli.main, options)
    assert result.exit_code == 0
    assert 'TIME_FORMAT="%H:%M %z"' in result.output


# -- Exception cases ------------------------------------------------------------


@pytest.mark.parametrize(
    "command, exception_detail",
    [
        (" @ 9pm 8 days ago", exceptions.InvalidWorkError.detail),
        ("Creating the world @ lolololol", exceptions.InvalidDateTimeError.detail),
        ("Walking the dog @ 5pm tomorrow", exceptions.DateTimeInFutureError.detail),
    ],
)
def test_invalid_input(runner: CliRunner, command: str, exception_detail: str) -> None:
    result = runner.invoke(cli.main, command)
    assert result.exit_code == 1
    assert exception_detail in result.output


@pytest.mark.parametrize(
    "flags, detail",
    [
        (
            ["--no-page", "--from", "3pm yesterday", "-t", "3pm 5 days ago"],
            exceptions.StartDateGreaterError.detail,
        ),
        (["--no-page", "--from", "3pm tomorrow"], exceptions.DateTimeInFutureError.detail),
        (["--no-page", "--count", "0"], exceptions.CannotFetchWorkError.detail),
    ],
)
def test_fetch_errors(runner: CliRunner, flags: list[str], detail: str) -> None:
    # First save a valid entry
    save_and_verify(runner, "doing taxes @ 9pm yesterday", "doing taxes")
    result = runner.invoke(cli.what, flags)
    assert result.exit_code == 1
    assert detail in result.output
