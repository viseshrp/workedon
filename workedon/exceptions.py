"""
workedon.exceptions
-----------------------
All exceptions used in the code base are defined here.
"""


class WorkedOnError(Exception):
    """
    Base exception. All other exceptions
    inherit from here.
    """

    detail = "An error occurred."

    def __init__(self, extra_detail=None):
        super().__init__()
        self.extra_detail = extra_detail

    def __str__(self):
        if self.extra_detail:
            return f"{self.detail} :: {self.extra_detail}"
        return self.detail


class CannotCreateSettingsError(WorkedOnError):
    """
    Exception raised if settings file could not be created
    """

    detail = "Unable to create settings file."


class CannotLoadSettingsError(WorkedOnError):
    """
    Exception raised if settings file could not be loaded
    """

    detail = "Unable to load settings file."


class InvalidWorkError(WorkedOnError):
    """
    Exception raised if the work text is empty
    """

    detail = "The provided work text is invalid."


class InvalidDateTimeError(WorkedOnError):
    """
    Exception raised if the given datetime string is invalid
    """

    detail = "The provided date/time is invalid. Please refer the docs for valid phrases."


class DateTimeInFutureError(WorkedOnError):
    """
    Exception raised if the given datetime is in the future
    """

    detail = "The provided date/time is in the future."


class StartDateAbsentError(WorkedOnError):
    """
    Exception raised if start date is not provided
    """

    detail = "Please provide a start date/time."


class StartDateGreaterError(WorkedOnError):
    """
    Exception raised if start date is greater than end date
    """

    detail = "The provided start date/time is greater than the end date/time."


class CannotSaveWorkError(WorkedOnError):
    """
    Exception raised if work could not be saved
    """

    detail = "Unable to save your work."


class CannotFetchWorkError(WorkedOnError):
    """
    Exception raised if work could not be fetched
    """

    detail = "Unable to fetch your work."
