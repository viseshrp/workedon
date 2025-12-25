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


def test_main_with_subcommand_returns_early(runner: CliRunner) -> None:
    result = runner.invoke(cli.main, ["what", "--no-page"])
    assert result.exit_code == 0


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


def test_fetch_last_returns_most_recent_entry(runner: CliRunner) -> None:
    save_and_verify(runner, "first thing @ 3 days ago", "first thing")
    save_and_verify(runner, "second thing @ yesterday", "second thing")

    result = runner.invoke(cli.what, ["--no-page", "--last"])
    verify_work_output(result, "second thing")
    assert "first thing" not in result.output


# -- Fetch by ID ----------------------------------------------------------------


def test_fetch_by_id(runner: CliRunner) -> None:
    description = "recording a demo"
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
            ["--since", "August 1 1947", "-r", "-n", "1"],
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
    ],
)
def test_save_and_fetch_others(runner: CliRunner, command: str, flag: list[str]) -> None:
    description = command.split(" @")[0]
    save_and_verify(runner, command, description)

    result = runner.invoke(cli.what, ["--no-page", *flag])
    verify_work_output(result, description)


def test_default_fetch_excludes_entries_older_than_week(runner: CliRunner) -> None:
    save_and_verify(runner, "ancient history @ 10 days ago", "ancient history")
    save_and_verify(runner, "fresh work @ yesterday", "fresh work")

    result = runner.invoke(cli.what, ["--no-page"])
    verify_work_output(result, "fresh work")
    assert "ancient history" not in result.output


# -- Deletion --------------------------------------------------------------------


def test_delete_work(runner: CliRunner) -> None:
    description = "watching Modern Family"
    timestamp = "@ 8:53am"
    save_and_verify(runner, f"{description} #season1 {timestamp}", description)

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
    assert result.output.startswith("Database schema version: ")


@pytest.mark.parametrize("options", [["--sqlite-version"]])
def test_sqlite_version(runner: CliRunner, options: list[str]) -> None:
    result = runner.invoke(cli.main, options)
    assert result.exit_code == 0
    assert result.output.startswith("SQLite version: ")


@pytest.mark.parametrize(
    "command, description",
    [
        # we need at least one row in the DB before truncating
        ("some one-off task", "some one-off task"),
    ],
)
def test_db_truncate(
    runner: CliRunner,
    command: str,
    description: str,
) -> None:
    save_result = runner.invoke(cli.main, command.split())
    assert save_result.exit_code == 0
    assert "Work saved." in save_result.output
    assert description in save_result.output

    truncate_result = runner.invoke(cli.main, ["--truncate-db"], input="y\n")
    assert truncate_result.exit_code == 0
    assert "Deletion successful." in truncate_result.output

    post_truncate = runner.invoke(cli.what, ["--no-page", "--last"])
    assert post_truncate.exit_code == 0
    assert "Nothing to show" in post_truncate.output


def test_db_truncate_declined(runner: CliRunner) -> None:
    # Save something so DB is non-empty:
    runner.invoke(cli.main, ["temporary", "job"])

    # Invoke "--truncate-db" but answer "n"
    result = runner.invoke(cli.main, ["--truncate-db"], input="n\n")
    # We expect exit_code==0 (Click returns 0 even if the user says “no”),
    # and no "Deletion successful."
    assert result.exit_code == 0
    assert "Deletion successful." not in result.output

    # There should still be data in the DB:
    still_there = runner.invoke(cli.what, ["--no-page", "--last"])
    assert still_there.exit_code == 0
    assert "temporary job" in still_there.output


# -- Settings -------------------------------------------------------


@pytest.mark.parametrize("options", [["--print-settings-path"]])
def test_conf_print_path(runner: CliRunner, options: list[str]) -> None:
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
        # (start > end) → StartDateGreaterError
        (
            ["--no-page", "--from", "3pm yesterday", "-t", "3pm 5 days ago"],
            exceptions.StartDateGreaterError.detail,
        ),
        # (start in the future) → DateTimeInFutureError
        (["--no-page", "--from", "3pm tomorrow"], exceptions.DateTimeInFutureError.detail),
        # (count == 0) → CannotFetchWorkError
        (["--no-page", "--count", "0"], exceptions.CannotFetchWorkError.detail),
        # <------ “--to” without any “--from” ------>
        (["--no-page", "--to", "3pm yesterday"], exceptions.StartDateAbsentError.detail),
    ],
)
def test_fetch_errors(runner: CliRunner, flags: list[str], detail: str) -> None:
    save_and_verify(runner, "doing taxes @ 9pm yesterday", "doing taxes")
    result = runner.invoke(cli.what, flags)
    assert result.exit_code == 1
    assert detail in result.output


# -- Tagging ------------------------------------------------------------


@pytest.mark.parametrize(
    "input_text, expected_tags",
    [
        ("coding new feature #dev", {"dev"}),
        ("daily standup #work #team", {"work", "team"}),
        ("writing unit tests #TDD #QA", {"tdd", "qa"}),
        ("prepping lunch #Home #MealPrep", {"home", "mealprep"}),
        ("empty tag test #", set()),  # should be ignored
        ("duplicate tags test #fun #fun #fun", {"fun"}),
    ],
)
def test_cli_tag_parsing_and_display(
    runner: CliRunner, input_text: str, expected_tags: set[str]
) -> None:
    result_save = runner.invoke(cli.main, input_text.split())
    assert result_save.exit_code == 0
    assert "Work saved." in result_save.output

    result_fetch = runner.invoke(cli.what, ["--no-page", "--last"])
    assert result_fetch.exit_code == 0

    for tag in expected_tags:
        assert tag.lower() in result_fetch.output.lower()


@pytest.mark.parametrize(
    "input_text, expected_tags",
    [
        ("tag with dash #in-progress", {"in-progress"}),
        ("tag with underscore #code_review", {"code_review"}),
        ("numeric tag #123", {"123"}),
        ("alphanumeric mix #r2d2", {"r2d2"}),
        ("non-word chars #cool! #$money", {"cool"}),  # `$money` ignored
        ("emoji tag #🔥", set()),  # emoji-only tag ignored
        ("weird spacing # spaced", {"spaced"}),  # space after `#` ignored
        ("back-to-back #one#two#three", {"one", "two", "three"}),  # should catch all
        ("URL in tag context #http123", {"http123"}),  # safe string
        ("mixed case tags #Dev #DEV #dev", {"dev"}),  # normalized
        ("invalid format tags ##double", {"double"}),  # invalid
        ("edge #", set()),  # empty tag
    ],
)
def test_weird_tag_parsing(runner: CliRunner, input_text: str, expected_tags: set[str]) -> None:
    result_save = runner.invoke(cli.main, input_text.split())
    assert result_save.exit_code == 0
    assert "Work saved." in result_save.output

    result_fetch = runner.invoke(cli.what, ["--no-page", "--last"])
    assert result_fetch.exit_code == 0

    for tag in expected_tags:
        assert tag.lower() in result_fetch.output.lower()

    if not expected_tags:
        assert "Tags:" not in result_fetch.output


@pytest.mark.parametrize(
    "save_cmd, tag_flag, expect_match",
    [
        ("working on #devtools", ["--tag", "devtools"], True),
        ("#in-progress cleanup", ["--tag", "in-progress"], True),
        ("writing code #DEV", ["--tag", "dev"], True),  # case-insensitive
        ("refactoring #code_review", ["--tag", "code_review"], True),
        ("invalid ##doubletag", ["--tag", "doubletag"], True),
        ("emoji #🔥", ["--tag", "🔥"], False),
        ("no tags here", ["--tag", "nothing"], False),
    ],
)
def test_cli_tag_filter(
    runner: CliRunner, save_cmd: str, tag_flag: list[str], expect_match: bool
) -> None:
    result_save = runner.invoke(cli.main, save_cmd.split())
    assert result_save.exit_code == 0

    result_fetch = runner.invoke(cli.what, ["--no-page", *tag_flag])
    if expect_match:
        assert "Date:" in result_fetch.output
    else:
        assert "Nothing to show" in result_fetch.output


def test_list_tags_outputs_saved_tags(runner: CliRunner) -> None:
    runner.invoke(cli.main, ["first", "tag", "#alpha"])
    runner.invoke(cli.main, ["second", "tag", "#beta"])

    result = runner.invoke(cli.main, ["--list-tags"])
    assert result.exit_code == 0
    assert "alpha" in result.output.lower()
    assert "beta" in result.output.lower()


# -- Duration ------------------------------------------------------------


@pytest.mark.parametrize(
    "input_text, expected_duration, xargs",
    [
        ("doing taxes [1h]", "Duration: 1.0 hr", ["--duration-unit", "hr"]),
        ("filing returns [1.5hr]", "Duration: 90.0 min", ["--duration-unit", "min"]),
        ("gym workout [90min]", "Duration: 1.5 hr", ["--duration-unit", "hr"]),
        ("long call [2.25hours]", "Duration: 2.25 hr", ["--duration-unit", "hr"]),
        ("fast errand [45m] [90m]", "Duration: 0.75 hr", ["--duration-unit", "hr"]),
        ("short nap [15MINS]", "Duration: 15.0 min", []),
    ],
)
def test_cli_duration_parsing_and_display(
    runner: CliRunner, input_text: str, expected_duration: str, xargs: list
) -> None:
    result_save = runner.invoke(cli.main, [*input_text.split(), *xargs])
    assert result_save.exit_code == 0
    assert "Work saved." in result_save.output
    assert expected_duration in result_save.output


@pytest.mark.parametrize(
    "input_text",
    [
        "broken input [3x]",
        "missing unit [123]",
        "non-numeric [abcmin]",
        "[1.2.3h]",
        "empty brackets []",
        "only unit [hrs]",
    ],
)
def test_cli_malformed_durations_are_ignored(runner: CliRunner, input_text: str) -> None:
    result_save = runner.invoke(cli.main, input_text.split())
    assert result_save.exit_code == 0
    assert "Work saved." in result_save.output

    result_fetch = runner.invoke(cli.what, ["--no-page", "--last"])
    assert result_fetch.exit_code == 0
    assert "Duration:" not in result_fetch.output


@pytest.mark.parametrize(
    "input_cmd, filter_flags, expect_match",
    [
        ("task1 [2h] @ 1pm", ["--duration", "=120m"], True),
        ("task2 [90m] @ 2pm", ["--duration", "<2h"], True),
        ("task3 [3h] @ 3pm", ["--duration", ">=3h"], True),
        ("task4 [60m] @ 4pm", ["--duration", "<=1h"], True),
        ("task5 [1.5h] @ 5pm", ["--duration", "=90m"], True),
        ("task6 [45m] @ 6pm", ["--duration", ">1h"], False),
        ("task7 [2h] @ 7pm", ["--duration", "<2h"], False),
    ],
)
def test_cli_duration_filter(
    runner: CliRunner, input_cmd: str, filter_flags: list[str], expect_match: bool
) -> None:
    result_save = runner.invoke(cli.main, input_cmd.split())
    assert result_save.exit_code == 0

    result_fetch = runner.invoke(cli.what, ["--no-page", *filter_flags])
    if expect_match:
        assert "Date:" in result_fetch.output
    else:
        assert "Nothing to show" in result_fetch.output


@pytest.mark.parametrize(
    "invalid_filter_flag",
    [
        ["--duration", "=>3h"],
        ["--duration", "3hors"],
        ["--duration", "3h<"],
        ["--duration", "3x"],
    ],
)
def test_invalid_duration_filter(runner: CliRunner, invalid_filter_flag: list[str]) -> None:
    result = runner.invoke(cli.what, ["--no-page", *invalid_filter_flag])
    assert result.exit_code == 1
    assert "Invalid duration" in result.output


def test_cli_duration_option_overrides_inline_value(runner: CliRunner) -> None:
    save_result = runner.invoke(cli.main, ["overridden task", "[30m]", "--duration", "2h"])
    verify_work_output(save_result, "overridden task")

    fetch_result = runner.invoke(cli.what, ["--no-page", "--last"])
    assert "Duration: 120.0 minutes" in fetch_result.output


def test_cli_duration_option_ignored_when_invalid(runner: CliRunner) -> None:
    save_result = runner.invoke(cli.main, ["keep inline", "[30m]", "--duration", "abc"])
    verify_work_output(save_result, "keep inline")

    fetch_result = runner.invoke(cli.what, ["--no-page", "--last"])
    assert "Duration: 30.0 minutes" in fetch_result.output
