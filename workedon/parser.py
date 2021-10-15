from dateparser import DateDataParser

from .exceptions import InvalidDateTimeError, DateTimeInFutureError
from .default_settings import DEFAULT_HOUR, DEFAULT_MINUTE, DATE_PARSER


class InputParser:
    def __init__(self):
        self._date_parser = DateDataParser(languages=["en"], settings=DATE_PARSER)

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
            # add default hour, minute if absent
            if parsed_dt.hour == 0:
                parsed_dt = parsed_dt.replace(hour=int(DEFAULT_HOUR))
            if parsed_dt.minute == 0:
                parsed_dt = parsed_dt.replace(minute=int(DEFAULT_MINUTE))
            # disallow future dt
            if parsed_dt > self._as_datetime("now"):
                raise DateTimeInFutureError
        else:
            parsed_dt = self._as_datetime("now")

        return work, parsed_dt
