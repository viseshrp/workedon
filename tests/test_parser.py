from datetime import timedelta

from freezegun import freeze_time
import pytest

from workedon.conf import settings
from workedon.exceptions import InvalidWorkError
from workedon.parser import InputParser
from workedon.utils import now


@pytest.fixture(autouse=True)
def configure_settings() -> None:
    # Ensure defaults are loaded so timezone-aware parsing works in unit tests.
    settings.configure()


def test_parse_datetime_defaults_to_now() -> None:
    parser = InputParser()
    assert parser.parse_datetime("") == now()


def test_parse_datetime_future_time_moves_to_previous_day() -> None:
    with freeze_time("2024-01-02 10:00:00"):
        parser = InputParser()
        parsed = parser.parse_datetime("11:30pm")
        assert parsed.hour == 23
        assert parsed.minute == 30
        assert parsed.date() == (now() - timedelta(days=1)).date()


def test_parse_duration_handles_hours_and_minutes() -> None:
    parser = InputParser()
    assert parser.parse_duration("[1.234h]") == 74.04
    assert parser.parse_duration("[ 45 MINs ]") == 45


def test_clean_work_strips_tags_and_duration() -> None:
    parser = InputParser()
    cleaned = parser.clean_work("  Fix bug [30m]   #dev   #QA  ")
    assert cleaned == "Fix bug"


def test_parse_requires_non_empty_work_text() -> None:
    parser = InputParser()
    with pytest.raises(InvalidWorkError):
        parser.parse("#devops #prod @ yesterday")


def test_parse_extracts_all_components() -> None:
    parser = InputParser()
    work, dt, duration, tags = parser.parse("Write docs [90m] #Dev #Docs @ yesterday")
    assert work == "Write docs"
    assert duration == 90
    assert tags == {"Dev", "Docs"}
    assert dt.date() == (now() - timedelta(days=1)).date()


def test_as_datetime_returns_none_when_parser_has_no_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parser = InputParser()
    monkeypatch.setattr(parser._date_parser, "get_date_data", lambda *_: None)
    assert parser._as_datetime("not a date") is None


def test_parse_duration_returns_none_for_unknown_unit() -> None:
    parser = InputParser()
    parser._DURATION_REGEX = r"\[\s*(\d+(?:\.\d+)?)\s*(sec)\s*\]"
    assert parser.parse_duration("[5 sec]") is None
