"""Console script for workedon."""

import click
from click_default_group import DefaultGroup

from . import __version__
from .utils import command_handler
from .workedon import save_work, fetch_work

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(
    cls=DefaultGroup,
    default_if_no_args=True,
    context_settings=CONTEXT_SETTINGS,
)
@click.version_option(
    __version__,
    "-v",
    "--version"
)
def main():
    """CLI utility for daily work logging"""
    pass


@main.command(default=True)
@click.argument(
    "work",
    metavar="<what_you_worked_on>",
    nargs=-1,
    required=False,
    type=click.STRING,
)
@command_handler
def stuff(work):
    """
    Save your work
    """
    save_work(work)


@main.command()
@click.option(
    "-f",
    "--from",
    "start_date",
    required=False,
    default="",
    type=click.STRING,
    help="start date-time to filter with"
)
@click.option(
    "-t",
    "--to",
    "end_date",
    required=False,
    default="",
    type=click.STRING,
    help="end date-time to filter with"
)
@command_handler
def what(start_date, end_date):
    """
    Fetch your saved work
    """
    fetch_work(start_date, end_date)


if __name__ == "__main__":
    main()
