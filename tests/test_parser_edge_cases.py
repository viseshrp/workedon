"""Additional edge case tests for the InputParser."""

from datetime import timedelta

from freezegun import freeze_time
import pytest

from workedon.exceptions import (
    DateTimeInFutureError,
    InvalidDateTimeError,
    InvalidWorkError,
)
from workedon.parser import InputParser
from workedon.utils import now


@pytest.fixture
def parser() -> InputParser:
    return InputParser()


# --- Edge cases for parse_datetime ---


@pytest.mark.parametrize(
    "input_str",
    [
        "tomorrow at 5pm",
        "next week",
        "in 3 days",
        "2099-12-31",
    ],
)
def test_parse_datetime_future_raises_error(parser: InputParser, input_str: str) -> None:
    with pytest.raises(DateTimeInFutureError):
        parser.parse_datetime(input_str)


@pytest.mark.parametrize(
    "input_str",
    [
        "!@#$%^&*()",
        "asdfghjkl",
        "random gibberish",
        "123abc456def",
    ],
)
def test_parse_datetime_invalid_string_raises_error(parser: InputParser, input_str: str) -> None:
    with pytest.raises(InvalidDateTimeError):
        parser.parse_datetime(input_str)


def test_parse_datetime_whitespace_only_returns_now(parser: InputParser) -> None:
    assert parser.parse_datetime("   ") == now()
    assert parser.parse_datetime("\t\n") == now()


@pytest.mark.parametrize(
    "input_str",
    [
        "midnight",
        "noon",
        "3am",
        "11:59pm",
        "00:00",
        "23:59",
    ],
)
def test_parse_datetime_various_time_formats(parser: InputParser, input_str: str) -> None:
    result = parser.parse_datetime(input_str)
    assert result <= now()


def test_parse_datetime_edge_of_midnight(parser: InputParser) -> None:
    with freeze_time("2024-01-15 00:01:00"):
        try:
            result = parser.parse_datetime("11:59pm")
        except DateTimeInFutureError:
            assert True
        else:
            assert result.hour == 23
            assert result.minute == 59
            assert result.date() == (now() - timedelta(days=1)).date()


@pytest.mark.parametrize(
    "relative_time",
    [
        "1 second ago",
        "30 seconds ago",
        "1 minute ago",
        "59 minutes ago",
        "1 hour ago",
        "23 hours ago",
    ],
)
def test_parse_datetime_relative_times(parser: InputParser, relative_time: str) -> None:
    result = parser.parse_datetime(relative_time)
    assert result <= now()


# --- Edge cases for parse_duration ---


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("[0.5h]", 30),
        ("[0.25hr]", 15),
        ("[0.1hours]", 6),
        ("[1000m]", 1000),
        ("[0.01h]", 0.6),
        ("[99999min]", 99999),
    ],
)
def test_parse_duration_edge_values(parser: InputParser, input_str: str, expected: float) -> None:
    assert parser.parse_duration(input_str) == expected


@pytest.mark.parametrize(
    "input_str",
    [
        "[]",
        "[h]",
        "[min]",
        "[hours]",
        "[minutes]",
        "[0h]",  # Valid but zero
    ],
)
def test_parse_duration_no_numeric_value(parser: InputParser, input_str: str) -> None:
    result = parser.parse_duration(input_str)
    assert result is None or result == 0


@pytest.mark.parametrize(
    "input_str",
    [
        "[1.2.3h]",
        "[1..5m]",
        "[.5.h]",
        "[-5h]",
        "[+3m]",
    ],
)
def test_parse_duration_malformed_numbers(parser: InputParser, input_str: str) -> None:
    assert parser.parse_duration(input_str) is None


@pytest.mark.parametrize(
    "input_str",
    [
        "[3x]",
        "[5d]",
        "[2s]",
        "[10k]",
        "[1.5days]",
    ],
)
def test_parse_duration_invalid_units(parser: InputParser, input_str: str) -> None:
    assert parser.parse_duration(input_str) is None


def test_parse_duration_multiple_brackets_uses_first(parser: InputParser) -> None:
    assert parser.parse_duration("[30m] [60m] [90m]") == 30


def test_parse_duration_case_insensitive(parser: InputParser) -> None:
    assert parser.parse_duration("[2H]") == 120
    assert parser.parse_duration("[2Hr]") == 120
    assert parser.parse_duration("[2HRS]") == 120
    assert parser.parse_duration("[30MIN]") == 30
    assert parser.parse_duration("[30Minutes]") == 30


def test_parse_duration_with_spaces(parser: InputParser) -> None:
    assert parser.parse_duration("[  2  h  ]") == 120
    assert parser.parse_duration("[\t30\tm\t]") == 30


def test_parse_duration_no_brackets(parser: InputParser) -> None:
    assert parser.parse_duration("30m") is None
    assert parser.parse_duration("2h") is None


# --- Edge cases for parse_tags ---


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("#tag1 #tag2 #tag3", {"tag1", "tag2", "tag3"}),
        ("#TAG #Tag #tag", {"TAG", "Tag", "tag"}),  # Case preserved
        ("#a #b #c #a #b", {"a", "b", "c"}),
        ("#123 #456", {"123", "456"}),
        ("#under_score #dash-tag", {"under_score", "dash-tag"}),
        ("#mix123abc", {"mix123abc"}),
    ],
)
def test_parse_tags_various_formats(parser: InputParser, input_str: str, expected: set) -> None:
    assert parser.parse_tags(input_str) == expected


@pytest.mark.parametrize(
    "input_str",
    [
        "no tags here",
        "has # space",
        "##",
        "###",
        "#",
    ],
)
def test_parse_tags_no_valid_tags(parser: InputParser, input_str: str) -> None:
    assert parser.parse_tags(input_str) == set()


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("#tag!", {"tag"}),  # Stops at special char
        ("#tag@email", {"tag"}),
        ("#tag.with.dots", {"tag"}),
        ("#tag(parentheses)", {"tag"}),
        ("#tag[brackets]", {"tag"}),
        ("#tag{braces}", {"tag"}),
    ],
)
def test_parse_tags_with_special_chars(parser: InputParser, input_str: str, expected: set) -> None:
    assert parser.parse_tags(input_str) == expected


def test_parse_tags_with_unicode(parser: InputParser) -> None:
    # Emoji and other unicode should not match
    assert parser.parse_tags("#🔥 #😀") == set()


def test_parse_tags_back_to_back(parser: InputParser) -> None:
    assert parser.parse_tags("#one#two#three") == {"one", "two", "three"}


def test_parse_tags_empty_string(parser: InputParser) -> None:
    assert parser.parse_tags("") == set()


# --- Edge cases for clean_work ---


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("work [30m] #tag", "work"),
        ("#tag1 #tag2 work", "work"),
        ("work #tag [60m]", "work"),
        ("[2h] #dev work #qa [30m]", "work [30m]"),
        ("  multiple    spaces  ", "multiple spaces"),
        ("\ttabs\tand\nnewlines\n", "tabs and newlines"),
    ],
)
def test_clean_work_removes_tags_and_duration(
    parser: InputParser, input_str: str, expected: str
) -> None:
    assert parser.clean_work(input_str) == expected


def test_clean_work_preserves_special_chars(parser: InputParser) -> None:
    assert parser.clean_work("work with @mentions") == "work with @mentions"
    assert parser.clean_work("work & more stuff") == "work & more stuff"
    assert parser.clean_work("work (in parens)") == "work (in parens)"


def test_clean_work_empty_after_cleaning(parser: InputParser) -> None:
    assert parser.clean_work("#tag1 #tag2 [30m]") == ""
    assert parser.clean_work("   [2h]   ") == ""


# --- Edge cases for parse (main method) ---


def test_parse_work_without_separator(parser: InputParser) -> None:
    work, dt, duration, tags = parser.parse("simple work")
    assert work == "simple work"
    assert dt == now()
    assert duration is None
    assert tags == set()


def test_parse_work_with_all_components(parser: InputParser) -> None:
    work, dt, duration, tags = parser.parse("complex work [90m] #dev #qa @ yesterday")
    assert work == "complex work"
    assert duration == 90
    assert tags == {"dev", "qa"}
    assert dt.date() == (now() - timedelta(days=1)).date()


def test_parse_separator_in_work_text(parser: InputParser) -> None:
    # Last @ should be the separator
    work, dt, _duration, _tags = parser.parse("email to john@example.com @ yesterday")
    assert work == "email to john@example.com"
    assert dt.date() == (now() - timedelta(days=1)).date()


def test_parse_multiple_separators(parser: InputParser) -> None:
    # Should partition on the last @
    work, dt, _duration, _tags = parser.parse("work @ 3pm @ yesterday")
    assert work == "work @ 3pm"
    assert dt.date() == (now() - timedelta(days=1)).date()


def test_parse_empty_work_after_cleaning_raises(parser: InputParser) -> None:
    with pytest.raises(InvalidWorkError):
        parser.parse("#tag [30m] @ yesterday")


def test_parse_separator_with_no_work_raises(parser: InputParser) -> None:
    with pytest.raises(InvalidWorkError):
        parser.parse("@ yesterday")


def test_parse_whitespace_only_raises(parser: InputParser) -> None:
    with pytest.raises(InvalidWorkError):
        parser.parse("   ")


def test_parse_multiple_durations_uses_first(parser: InputParser) -> None:
    _work, _dt, duration, _tags = parser.parse("work [30m] [60m] [90m]")
    assert duration == 30


def test_parse_preserves_work_punctuation(parser: InputParser) -> None:
    work, _, _, _ = parser.parse("Work! With? Punctuation.")
    assert work == "Work! With? Punctuation."


@pytest.mark.parametrize(
    "input_str",
    [
        "work @ tomorrow",
        "work @ next week",
        "work @ in 5 days",
    ],
)
def test_parse_future_datetime_raises(parser: InputParser, input_str: str) -> None:
    with pytest.raises(DateTimeInFutureError):
        parser.parse(input_str)


def test_parse_invalid_datetime_raises(parser: InputParser) -> None:
    with pytest.raises(InvalidDateTimeError):
        parser.parse("work @ gibberish datetime")


# --- Boundary conditions ---


def test_parse_extremely_long_work_text(parser: InputParser) -> None:
    long_text = "a" * 10000
    work, _, _, _ = parser.parse(long_text)
    assert work == long_text


def test_parse_many_tags(parser: InputParser) -> None:
    tags_str = " ".join(f"#tag{i}" for i in range(100))
    _work, _, _, tags = parser.parse(f"work {tags_str}")
    assert len(tags) == 100


def test_parse_very_precise_duration(parser: InputParser) -> None:
    _work, _, duration, _ = parser.parse("work [1.123456789h]")
    assert duration == 67.41  # Rounded to 2 decimals


def test_parse_zero_duration(parser: InputParser) -> None:
    _work, _, duration, _ = parser.parse("work [0h]")
    assert duration == 0
