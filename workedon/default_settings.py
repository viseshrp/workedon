from . import __version__

VERSION = __version__

TIME_ZONE = "UTC"

DEFAULT_HOUR = "09"

DEFAULT_MINUTE = "00"

DATE_FORMAT = "%m-%d-%Y"

TIME_FORMAT = "%H:%M"

DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

DATE_PARSER = {
    "STRICT_PARSING": False,
    "NORMALIZE": True,
    "RETURN_AS_TIMEZONE_AWARE": True,
    "PREFER_DATES_FROM": "past",
}
