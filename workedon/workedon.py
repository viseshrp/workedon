"""Main module."""
import datetime

import click
from peewee import chunked

from .exceptions import CannotSaveWorkError, CannotFetchWorkError, StartDateAbsentError
from .models import Work, init_db
from .parser import parser
from .utils import now, to_internal_dt

try:
    from backports import zoneinfo
except ImportError:
    import zoneinfo

WORK_CHUNK_SIZE = 100


def save_work(work):
    """
    Save work from user input
    """
    work_desc = " ".join(work)
    text, dt = parser.parse(work_desc)
    data = {"work": text}
    if dt:
        data["timestamp"] = to_internal_dt(dt)
    try:
        with init_db():
            w = Work.create(**data)
            click.echo("Work saved.")
            click.echo(w)
    except Exception as e:
        raise CannotSaveWorkError(extra_detail=str(e))


def _generate_work(result):
    """
    Fetch work in chunks, loop
    and yield one at a time for
    display.
    """
    for work_set in chunked(result, WORK_CHUNK_SIZE):
        for work in work_set:
            yield work


def _get_date_range(start_date, end_date, period):
    curr_dt = now()
    start = curr_dt - datetime.timedelta(days=7)
    end = curr_dt
    if period:
        # past week is the default
        if period == "yesterday":
            start = parser.parse_datetime("12am yesterday")
            end = parser.parse_datetime("12am today") - datetime.timedelta(seconds=1)
        elif period == "today":
            start = parser.parse_datetime("12am today")
        elif period == "day":  # past 24 hours
            start = parser.parse_datetime("yesterday")
        elif period == "month":  # past month
            start = parser.parse_datetime("1 month ago")
        elif period == "year":  # past year
            start = parser.parse_datetime("1 year ago")
    else:
        # need a start to avoid fetching everything since
        # the beginning of time.
        if not start_date and end_date:
            raise StartDateAbsentError
        if start_date:
            start = parser.parse_datetime(start_date)
        if end_date:
            end = parser.parse_datetime(end_date)

    return to_internal_dt(start), to_internal_dt(end)


def fetch_work(count, start_date, end_date, period):
    """
    Fetch saved work filtered based on user input
    """
    try:
        if count:
            work_set = Work.select().limit(count)
        else:
            start, end = _get_date_range(start_date, end_date, period)
            work_set = Work.select().where(
                (Work.timestamp >= start) & (Work.timestamp <= end)
            )
        # order by timestamp descending
        work_set = work_set.order_by(Work.timestamp.desc())
        # fetch from db now.
        with init_db():
            count = work_set.count()
            if count > 1:
                gen = work_set.iterator()
                click.echo_via_pager(_generate_work(gen))
            elif count == 1:
                click.echo(work_set[0])
            else:
                click.echo("Nothing to show, slacker.")
    except Exception as e:
        raise CannotFetchWorkError(extra_detail=str(e))
