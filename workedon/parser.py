from __future__ import annotations

from datetime import datetime

from dateparser import DateDataParser

from .exceptions import DateTimeInFutureError, InvalidDateTimeError, InvalidWorkError
from .utils import now


class InputParser:
    _date_parser: DateDataParser

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

    def parse_datetime(self, date_time: str) -> datetime | None:
        dt = date_time.strip()
        if not dt:
            return None
        parsed_dt = self._as_datetime(dt)
        if not parsed_dt:
            raise InvalidDateTimeError
        if parsed_dt > now():
            raise DateTimeInFutureError
        return parsed_dt

    def parse(self, work_desc: str) -> tuple[str, datetime | None]:
        if "@" in work_desc:
            work, _, date_time = work_desc.rpartition("@")
        else:
            work, date_time = work_desc, ""
        work = work.strip()
        date_time = date_time.strip()
        if not work:
            raise InvalidWorkError
        date_time_parsed = self.parse_datetime(date_time)
        return work, date_time_parsed
