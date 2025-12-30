from __future__ import annotations

from datetime import datetime, timedelta
import re
from typing import Final

from dateparser.date import DateDataParser

from .exceptions import DateTimeInFutureError, InvalidDateTimeError, InvalidWorkError
from .utils import now


class InputParser:
    _date_parser: DateDataParser | None = None
    _WORK_DATE_SEPARATOR: Final[str] = "@"
    _TAG_REGEX: Final[str] = r"#([\w\d_-]+)"
    _DURATION_REGEX: Final[str] = r"\[\s*(\d+(?:\.\d+)?)\s*(h|hr|hrs|hours|m|min|mins|minutes)\s*\]"

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
        if self._date_parser is None:
            raise RuntimeError("_date_parser must be initialized before use")
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
        current = now()
        # workaround a dateparser bug: even though we set PREFER_DATES_FROM to "past",
        # it sometimes still returns a future date when only time is given.
        # If parsed time is on the same day and still in the future, shift to previous day
        if parsed_dt.date() == current.date() and parsed_dt > current:
            parsed_dt = parsed_dt - timedelta(days=1)
        if parsed_dt > current:
            raise DateTimeInFutureError()
        return parsed_dt

    def parse_duration(self, input_str: str) -> float | None:
        """
        Extracts the first duration from the input_str string and returns it in minutes.
        """
        match = re.search(self._DURATION_REGEX, input_str, flags=re.IGNORECASE)
        if not match:
            return None
        value, unit = match.groups()
        value = float(value)
        unit = unit.lower()
        if unit in {"h", "hr", "hrs", "hours"}:
            return round(value * 60, 2)
        elif unit in {"m", "min", "mins", "minutes"}:
            return value
        return None

    def parse_tags(self, input_str: str) -> set[str]:
        return set(re.findall(self._TAG_REGEX, input_str))

    def clean_work(self, work: str) -> str:
        """
        Cleans the work string by removing any duration and tags.
        """
        # remove duration
        work = re.sub(self._DURATION_REGEX, "", work, count=1, flags=re.IGNORECASE).strip()
        # remove tags
        work = re.sub(self._TAG_REGEX, "", work)
        # collapse extra spaces
        work = re.sub(r"\s+", " ", work).strip()
        return work

    def parse(self, work_desc: str) -> tuple[str, datetime, float | None, set[str]]:
        if self._WORK_DATE_SEPARATOR in work_desc:
            work, _, date_time = work_desc.rpartition(self._WORK_DATE_SEPARATOR)
        else:
            work, date_time = work_desc, ""

        work = work.strip()
        dt = self.parse_datetime(date_time.strip())
        duration = self.parse_duration(work)
        tags = self.parse_tags(work)
        work = self.clean_work(work)
        if not work:
            raise InvalidWorkError

        return work, dt, duration, tags
