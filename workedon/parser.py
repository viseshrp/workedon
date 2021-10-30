import sys

from dateparser import DateDataParser

from .conf import settings
from .exceptions import InvalidDateTimeError, DateTimeInFutureError

if sys.version_info >= (3, 9):
    import zoneinfo
else:
    from backports import zoneinfo


class InputParser:
    DATE_PARSER_SETTINGS = {
        "STRICT_PARSING": False,
        "NORMALIZE": True,
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "past",
    }

    def __init__(self):
        self._date_parser = DateDataParser(languages=["en"], settings=self.DATE_PARSER_SETTINGS)

    def _as_datetime(self, date_time):
        dt_obj = self._date_parser.get_date_data(date_time)
        if dt_obj:
            return dt_obj["date_obj"]

    def parse(self, work_desc):
        if "@" in work_desc:
            # split at the last @
            work, _, date_time = work_desc.rpartition("@")
        else:
            work, date_time = (work_desc, "")
        work, date_time = (work.strip(), date_time.strip())
        if date_time:
            parsed_dt = self._as_datetime(date_time)
            if not parsed_dt:
                raise InvalidDateTimeError
            # disallow future dt
            if parsed_dt > self._as_datetime("now"):
                raise DateTimeInFutureError
        else:
            parsed_dt = self._as_datetime("now")
        # convert to internal time for storage
        parsed_dt = parsed_dt.astimezone(zoneinfo.ZoneInfo(settings.internal_tz))
        return work, parsed_dt


parser = InputParser()
