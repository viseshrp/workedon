import re

from dateparser import DateDataParser

from .exceptions import DateTimeInFutureError, InvalidDateTimeError, InvalidWorkError
from .utils import now


class InputParser:
    WORK_DATE_SEPARATOR = "@"
    TAG_REGEX = r"#([\w\d_-]+)"

    def __init__(self):
        self._date_parser = DateDataParser(
            languages=["en"],
            settings={
                "STRICT_PARSING": False,
                "NORMALIZE": True,
                "RETURN_AS_TIMEZONE_AWARE": True,
                "PREFER_DATES_FROM": "past",
                "RELATIVE_BASE": now(),
            },
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
        if parsed_dt > now():
            raise DateTimeInFutureError
        return parsed_dt

    def parse_tags(self, work):
        return set(re.findall(self.TAG_REGEX, work))

    def parse(self, work_desc):
        if self.WORK_DATE_SEPARATOR in work_desc:
            work, _, date_time = work_desc.rpartition(self.WORK_DATE_SEPARATOR)
        else:
            work, date_time = (work_desc, "")
        work = work.strip()
        date_time = date_time.strip()
        if not work:
            raise InvalidWorkError
        tags = self.parse_tags(work)
        date_time = self.parse_datetime(date_time)
        return work, date_time, tags
