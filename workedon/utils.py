import sys
from functools import wraps

import click

from .conf import settings

if sys.version_info >= (3, 9):
    import zoneinfo
else:
    from backports import zoneinfo


def pretty_print_work(func):
    @wraps(func)
    def pretty(*args, **kwargs):
        work = func(*args, **kwargs)
        click.secho(f"\nID: {work.uuid}", fg="green")
        user_time = work.created.astimezone(zoneinfo.ZoneInfo(settings.user_tz))
        click.echo(f"Date: {user_time.strftime(f'{settings.DATETIME_FORMAT}')}\n")
        click.secho(f"    {work.work}\n", bold=True, fg="white")

    return pretty
