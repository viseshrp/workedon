from functools import wraps

import click

from .conf import settings


def pretty_print_work(func):
    @wraps(func)
    def pretty(*args, **kwargs):
        work = func(*args, **kwargs)
        click.secho(f"\nID: {work.uuid}", fg="green")
        click.echo(f"Date: {work.created.strftime(f'{settings.DATETIME_FORMAT}')}\n")
        click.secho(f"    {work.work}\n", bold=True, fg="white")

    return pretty
