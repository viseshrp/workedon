import pytest

from workedon import exceptions


@pytest.mark.parametrize(
    "exc_cls, detail",
    [
        (exceptions.DBInitializationError, "Unable to initialize the database."),
        (exceptions.CannotCreateSettingsError, "Unable to create settings file."),
        (exceptions.CannotLoadSettingsError, "Unable to load settings file."),
        (exceptions.InvalidWorkError, "The provided work text is invalid."),
        (
            exceptions.InvalidDateTimeError,
            "The provided date/time is invalid. Please refer the docs for valid phrases.",
        ),
        (exceptions.DateTimeInFutureError, "The provided date/time is in the future."),
        (exceptions.StartDateAbsentError, "Please provide a start date/time."),
        (
            exceptions.StartDateGreaterError,
            "The provided start date/time is greater than the end date/time.",
        ),
        (exceptions.CannotSaveWorkError, "Unable to save your work."),
        (exceptions.CannotFetchWorkError, "Unable to fetch your work."),
    ],
)
def test_exception_details_and_string_formatting(
    exc_cls: type[exceptions.WorkedOnError], detail: str
) -> None:
    assert str(exc_cls()) == detail
    assert str(exc_cls(extra_detail="extra")) == f"{detail} :: extra"
    assert str(exc_cls(extra_detail="")) == detail
