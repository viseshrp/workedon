"""Main module."""
from functools import wraps

import click

from .conf import settings
from .exceptions import CannotSaveWorkError, CannotFetchWorkError
from .models import Work, init_db
from .parser import parser
from .utils import to_internal_tz

try:
    from backports import zoneinfo
except ImportError:
    import zoneinfo


def pretty_print(func):
    @wraps(func)
    def pretty(*args, **kwargs):
        work_list = func(*args, **kwargs)
        if not isinstance(work_list, list):
            work_list = [work_list]
        for work in work_list:
            click.secho(f"\nid: {work.uuid}", fg="green")
            user_time = work.timestamp.astimezone(zoneinfo.ZoneInfo(settings.user_tz))
            click.echo(f"Date: {user_time.strftime(f'{settings.DATETIME_FORMAT}')}\n")
            click.secho(f"    {work.work}\n", bold=True, fg="white")

    return pretty


@pretty_print
def save_work(work):
    work_desc = " ".join(work)
    text, dt = parser.parse(work_desc)
    timestamp = to_internal_tz(dt)
    try:
        with init_db():
            w = Work.create(work=text, timestamp=timestamp)
            return w
    except Exception as e:
        raise CannotSaveWorkError(extra_detail=str(e))
