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
@click.option(
    "-d",
    "--past-day",
    "period",
    flag_value="day",
    is_flag=True,
    help="Fetch work done in the past 24 hours"
)
@click.option(
    "-w",
    "--past-week",
    "period",
    flag_value="week",
    is_flag=True,
    help="Fetch work done in the past week"
)
@click.option(
    "-m",
    "--past-month",
    "period",
    flag_value="month",
    is_flag=True,
    help="Fetch work done in the past month"
)
@click.option(
    "-y",
    "--past-year",
    "period",
    flag_value="year",
    is_flag=True,
    help="Fetch work done in the past year"
)
@click.option(
    "-e",
    "--yesterday",
    "period",
    flag_value="yesterday",
    is_flag=True,
    help="Fetch work done yesterday"
)
@click.option(
    "-o",
    "--today",
    "period",
    flag_value="today",
    is_flag=True,
    help="Fetch work done today"
)
@command_handler
def what(start_date, end_date, period):
    """
    Fetch your saved work
    """
    fetch_work(start_date, end_date, period)


if __name__ == "__main__":
    main()
