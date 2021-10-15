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

    def __str__(self):
        return str(self.detail)


class DateTimeInFutureError(WonException):
    """
    Exception raised if the given datetime is in the future
    """

    detail = "The provided date/time is in the future."


class InvalidDateTimeError(WonException):
    """
    Exception raised if the given datetime is in the future
    """

    detail = (
        "The provided date/time is invalid. Please refer the docs for valid phrases."
    )
