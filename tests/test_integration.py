"""Integration tests covering complete workflows."""

from datetime import datetime
import zoneinfo

from click.testing import CliRunner
from freezegun import freeze_time
import pytest

from workedon import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_full_workflow_save_modify_fetch_delete(runner: CliRunner) -> None:
    # Save work
    save_result = runner.invoke(cli.main, ["working on feature #dev [2h] @ yesterday"])
    assert save_result.exit_code == 0
    assert "Work saved." in save_result.output

    # Fetch by tag
    fetch_result = runner.invoke(cli.what, ["--no-page", "--tag", "dev"])
    assert fetch_result.exit_code == 0
    assert "working on feature" in fetch_result.output

    # Fetch by duration
    duration_result = runner.invoke(cli.what, ["--no-page", "--duration", "=2h"])
    assert duration_result.exit_code == 0
    assert "working on feature" in duration_result.output

    # Delete
    delete_result = runner.invoke(cli.what, ["--no-page", "--tag", "dev", "--delete"], input="y")
    assert delete_result.exit_code == 0
    assert "deleted successfully" in delete_result.output

    # Verify deletion
    verify_result = runner.invoke(cli.what, ["--no-page", "--tag", "dev"])
    assert verify_result.exit_code == 0
    assert "Nothing to show" in verify_result.output


def test_multiple_tags_filtering(runner: CliRunner) -> None:
    # Save work with multiple tags
    runner.invoke(cli.main, ["task1 #dev #frontend @ 1pm yesterday"])
    runner.invoke(cli.main, ["task2 #dev #backend @ 2pm yesterday"])
    runner.invoke(cli.main, ["task3 #qa #frontend @ 3pm yesterday"])

    # Filter by single tag
    dev_result = runner.invoke(cli.what, ["--no-page", "--tag", "dev", "--yesterday"])
    assert "task1" in dev_result.output
    assert "task2" in dev_result.output
    assert "task3" not in dev_result.output

    # Filter by multiple tags (OR logic)
    multi_result = runner.invoke(
        cli.what, ["--no-page", "--tag", "dev", "--tag", "frontend", "--yesterday"]
    )
    assert "task1" in multi_result.output
    assert "task2" in multi_result.output
    assert "task3" in multi_result.output


def test_duration_with_timezone_changes(runner: CliRunner) -> None:
    # Save in one timezone
    runner.invoke(cli.main, ["work [90m] @ 3pm yesterday", "--time-zone", "UTC"])

    # Fetch in different timezone
    result = runner.invoke(cli.what, ["--no-page", "--last", "--time-zone", "Asia/Tokyo"])
    assert result.exit_code == 0
    assert "Duration:" in result.output


def test_pagination_with_large_dataset(runner: CliRunner) -> None:
    # Create many entries
    for i in range(50):
        runner.invoke(cli.main, [f"work item {i} @ {i} hours ago"])

    # Fetch without pagination
    no_page = runner.invoke(cli.what, ["--no-page", "--count", "50"])
    assert no_page.exit_code == 0

    # Fetch with pagination (default behavior, harder to test)
    with_page = runner.invoke(cli.what, ["--count", "50"])
    assert with_page.exit_code == 0


def test_edge_case_midnight_boundary(runner: CliRunner) -> None:
    # Save at midnight
    runner.invoke(cli.main, ["midnight task @ 12:00am"])

    # Should appear in today's results
    today_result = runner.invoke(cli.what, ["--no-page", "--today"])
    assert "midnight task" in today_result.output


@freeze_time("2024-01-10 15:00:00")
def test_complex_datetime_parsing(runner: CliRunner) -> None:
    fmt = "%Y-%m-%d %H:%M %z"
    tz = zoneinfo.ZoneInfo("UTC")
    test_cases = [
        ("meeting @ 3pm 5 days ago", datetime(2024, 1, 5, 15, 0, tzinfo=tz)),
        ("call @ 9:30am yesterday", datetime(2024, 1, 9, 9, 30, tzinfo=tz)),
        ("email @ noon 3 days ago", datetime(2024, 1, 7, 12, 0, tzinfo=tz)),
        ("standup @ 10am this week", datetime(2024, 1, 10, 10, 0, tzinfo=tz)),
    ]
    env = {"WORKEDON_TIME_ZONE": "UTC", "WORKEDON_DATETIME_FORMAT": fmt}

    for case, expected_dt in test_cases:
        result = runner.invoke(cli.main, case.split(), env=env)
        assert result.exit_code == 0
        assert "Work saved." in result.output
        assert f"Date: {expected_dt.strftime(fmt)}" in result.output
