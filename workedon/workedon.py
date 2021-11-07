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
    for work_set in chunked(result, 100):
        for work in work_set:
            yield work


def fetch_work(start_date, end_date):
    """
    Fetch saved work filtered based on user input
    """
    start = parser.parse_datetime(start_date)
    end = parser.parse_datetime(end_date)
    if not start and end:
        raise StartDateAbsentError
    if not start:
        # default is 1 week ago
        start = now() - datetime.timedelta(days=7)
    if not end:
        # default is now
        end = now()
    start = to_internal_dt(start)
    end = to_internal_dt(end)
    try:
        with init_db():
            works = Work.select().where((Work.timestamp >= start) & (Work.timestamp <= end)).order_by(
                Work.timestamp.desc())
            count = works.count()
            if count > 1:
                gen = works.iterator()
                click.echo_via_pager(_generate_work(gen))
            elif count == 1:
                click.echo(works[0])
            else:
                click.echo("Nothing to show, slacker.")
    except Exception as e:
        raise CannotFetchWorkError(extra_detail=str(e))
