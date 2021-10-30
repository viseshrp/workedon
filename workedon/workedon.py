"""Main module."""
import sys
from functools import wraps

import click

from .conf import settings
from .db import DBManager
from .exceptions import CannotSaveWorkError
from .parser import parser
from .utils import get_unique_hash

if sys.version_info >= (3, 9):
    import zoneinfo
else:
    from backports import zoneinfo


class Work:
    db = DBManager()

    def __init__(self, work, created):
        self.uuid = get_unique_hash()
        self.work = work
        self.created = created

    def save(self):
        try:
            self.db.create(uuid=self.uuid, work=self.work, created=self.created)
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
                click.secho(f"\nID: {work.uuid}", fg="green")
                user_time = work.created.astimezone(zoneinfo.ZoneInfo(settings.user_tz))
                click.echo(f"Date: {user_time.strftime(f'{settings.DATETIME_FORMAT}')}\n")
                click.secho(f"    {work.work}\n", bold=True, fg="white")

        return pretty


@Work.pretty_print
def save_work(work):
    work_desc = " ".join(work)
    text, dt = parser.parse(work_desc)
    w = Work(text, dt)
    w.save()
    return w
