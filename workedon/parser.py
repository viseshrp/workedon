from dateparser import DateDataParser

from .exceptions import InvalidDateTimeError, DateTimeInFutureError, InvalidWorkError
from .utils import now


class InputParser:
    LANGUAGES = ["en"]
    DATE_PARSER_SETTINGS = {
        "STRICT_PARSING": False,
        "NORMALIZE": True,
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "past",
        "RELATIVE_BASE": now(),
    }

    def __init__(self):
        self._date_parser = DateDataParser(
            languages=self.LANGUAGES, settings=self.DATE_PARSER_SETTINGS
        )

    def _as_datetime(self, date_time):
        dt_obj = self._date_parser.get_date_data(date_time)
        if dt_obj:
            return dt_obj["date_obj"]

    def parse_datetime(self, date_time):
        dt = date_time.strip()
        if not dt:
            return None
        parsed_dt = self._as_datetime(dt)
        if not parsed_dt:
            raise InvalidDateTimeError
        if parsed_dt > self._as_datetime("now"):
            raise DateTimeInFutureError
        return parsed_dt

    def parse(self, work_desc):
        if "@" in work_desc:
            work, _, date_time = work_desc.rpartition("@")
        else:
            work, date_time = (work_desc, "")
        work = work.strip()
        date_time = date_time.strip()
        if not work:
            raise InvalidWorkError
        date_time = self.parse_datetime(date_time)
        return work, date_time


parser = InputParser()
