"""Main module."""
import datetime
import sys
from datetime import datetime
from functools import wraps

import click

from .conf import settings
from .db import DBManager
from .exceptions import CannotSaveWorkError
from .parser import parser
from .utils import get_unique_hash, to_internal_tz

if sys.version_info >= (3, 9):
    import zoneinfo
else:
    from backports import zoneinfo


class Work:
    db = DBManager()

    def __init__(self, work, timestamp, created):
        self.uuid = get_unique_hash()
        self.work = work
        # convert to internal timezone for storage
        self.timestamp = to_internal_tz(timestamp)
        self.created = to_internal_tz(created)

    def save(self):
        try:
            self.db.create(uuid=self.uuid, work=self.work, timestamp=self.timestamp, created=self.created)
        except Exception as e:
            raise CannotSaveWorkError(extra_detail=str(e))

    @staticmethod
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


@Work.pretty_print
def save_work(work):
    created = datetime.now(zoneinfo.ZoneInfo(settings.user_tz))
    work_desc = " ".join(work)
    text, timestamp = parser.parse(work_desc)
    w = Work(text, timestamp, created)
    w.save()
    return w
