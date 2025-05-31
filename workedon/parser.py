from __future__ import annotations

from datetime import datetime
import re
from typing import Final

from dateparser.date import DateDataParser

from .exceptions import DateTimeInFutureError, InvalidDateTimeError, InvalidWorkError
from .utils import now


class InputParser:
    _date_parser: DateDataParser = None
    _WORK_DATE_SEPARATOR: Final[str] = "@"
    _TAG_REGEX: Final[str] = r"#([\w\d_-]+)"

    def __init__(self) -> None:
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

    def _as_datetime(self, date_time: str) -> datetime | None:
        dt_obj = self._date_parser.get_date_data(date_time)
        if dt_obj:
            date_obj: datetime = dt_obj["date_obj"]
            return date_obj
        return None

    def parse_datetime(self, date_time: str) -> datetime:
        dt = date_time.strip()
        # empty date_time is a no-op: return “now” so callers always get a datetime.
        if not dt:
            return now()
        parsed_dt = self._as_datetime(dt)
        if not parsed_dt:
            raise InvalidDateTimeError()
        if parsed_dt > now():
            raise DateTimeInFutureError()
        return parsed_dt

    def parse_tags(self, work: str) -> set[str]:
        return set(re.findall(self._TAG_REGEX, work))

    def parse(self, work_desc: str) -> tuple[str, datetime, set[str]]:
        if self._WORK_DATE_SEPARATOR in work_desc:
            work, _, date_time = work_desc.rpartition(self._WORK_DATE_SEPARATOR)
        else:
            work, date_time = work_desc, ""

        work = work.strip()
        date_time = date_time.strip()
        tags = self.parse_tags(work)
        # remove any "#tag" tokens from the work string
        work = re.sub(self._TAG_REGEX, "", work)
        # collapse extra spaces
        work = re.sub(r"\s+", " ", work).strip()
        if not work:
            raise InvalidWorkError

        dt = self.parse_datetime(date_time)
        return work, dt, tags
