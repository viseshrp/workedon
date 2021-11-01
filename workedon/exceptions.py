"""
workedon.exceptions
-----------------------
All exceptions used in the code base are defined here.
"""


class WonException(Exception):
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


class DateTimeInFutureError(WonException):
    """
    Exception raised if the given datetime is in the future
    """

    detail = "The provided date/time is in the future"


class InvalidWorkError(WonException):
    """
    Exception raised if the work text is empty
    """

    detail = "The provided work text is empty"


class InvalidDateTimeError(WonException):
    """
    Exception raised if the given datetime is in the future
    """

    detail = "The provided date/time is invalid. Please refer the docs for valid phrases"


class CannotCreateSettingsError(WonException):
    """
    Exception raised if settings file could not be created
    """

    detail = "Unable to create settings file"


class CannotLoadSettingsError(WonException):
    """
    Exception raised if settings file could not be loaded
    """

    detail = "Unable to load settings file"


class CannotSaveWorkError(WonException):
    """
    Exception raised if settings file could not be loaded
    """

    detail = "Unable to save your work"

