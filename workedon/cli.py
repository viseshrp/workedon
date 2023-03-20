"""Console script for workedon."""

import warnings

import click
from click_default_group import DefaultGroup

from . import __version__
from .models import Work, get_or_create_db
from .utils import get_db_path, load_settings
from .workedon import fetch_work, save_work

warnings.filterwarnings("ignore")
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(
    cls=DefaultGroup,
    context_settings=CONTEXT_SETTINGS,
)
@click.version_option(__version__, "-v", "--version")
def main():
    """
    Work logging from the comfort of your shell.

    \b
    Example usages:
    1. Logging work:
    workedon studying for the SAT @ June 2010
    workedon pissing my wife off @ 2pm yesterday
    workedon painting the garage

    \b
    2. Fetching work:
    workedon what
    workedon what --from "2pm yesterday" --to "9am today"
    workedon what --today
    workedon what --past-month
    """
    pass


@main.command(default=True)
@click.argument(
    "stuff",
    metavar="<what_you_worked_on>",
    nargs=-1,
    required=False,
    type=click.STRING,
)
@load_settings
def workedon(stuff):
    """
    What you worked on, with optional date/time - see examples.
    """
    save_work(stuff)


@main.command()
@click.option(
    "-r",
    "--reverse",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Reverse order while sorting.",
)
@click.option("-n", "--count", required=False, type=click.INT, help="Number of entries to return.")
@click.option(
    "-s",
    "--last",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Fetch the last thing you worked on",
)
@click.option(
    "-i",
    "--id",
    "work_id",
    required=False,
    default="",
    type=click.STRING,
    help="id to fetch with.",
)
@click.option(
    "-f",
    "--from",
    "start_date",
    required=False,
    default="",
    type=click.STRING,
    help="Start date-time to filter with.",
)
@click.option(
    "-t",
    "--to",
    "end_date",
    required=False,
    default="",
    type=click.STRING,
    help="End date-time to filter with.",
)
@click.option(
    "--since",
    required=False,
    default="",
    type=click.STRING,
    help="Fetch work done since a specified date-time in the past.",
)
@click.option(
    "-d",
    "--past-day",
    "period",
    flag_value="day",
    is_flag=True,
    help="Fetch work done in the past 24 hours.",
)
@click.option(
    "-w",
    "--past-week",
    "period",
    flag_value="week",
    is_flag=True,
    help="Fetch work done in the past week.",
)
@click.option(
    "-m",
    "--past-month",
    "period",
    flag_value="month",
    is_flag=True,
    help="Fetch work done in the past month.",
)
@click.option(
    "-y",
    "--past-year",
    "period",
    flag_value="year",
    is_flag=True,
    help="Fetch work done in the past year.",
)
@click.option(
    "-e",
    "--yesterday",
    "period",
    flag_value="yesterday",
    is_flag=True,
    help="Fetch work done yesterday.",
)
@click.option(
    "-o",
    "--today",
    "period",
    flag_value="today",
    is_flag=True,
    help="Fetch work done today.",
)
@click.option(
    "--on",
    required=False,
    type=click.STRING,
    help="Fetch work done on a particular date/day.",
)
@click.option(
    "--at",
    required=False,
    type=click.STRING,
    help="Fetch work done at a particular time on a particular date/day.",
)
@click.option(
    "--delete",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Delete fetched work.",
)
@click.option(
    "-g",
    "--no-page",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Don't page the output.",
)
@click.option(
    "-l",
    "--text-only",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Output the work log text only.",
)
@load_settings
def what(
    count,
    last,
    work_id,
    start_date,
    end_date,
    since,
    period,
    on,
    at,
    delete,
    no_page,
    reverse,
    text_only,
):
    """
    Fetch logged work.
    """
    if count is None and last:
        count = 1
    fetch_work(
        count,
        work_id,
        start_date,
        end_date,
        since,
        period,
        on,
        at,
        delete,
        no_page,
        reverse,
        text_only,
    )


@main.command()
@click.option(
    "--print-path",
    "db_path",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Print the location of the database file.",
)
@click.option(
    "--vacuum",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Execute the VACUUM command on the database to reclaim some space.",
)
@click.option(
    "--truncate",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Delete all data since the beginning of time.",
)
@load_settings
def db(db_path, vacuum, truncate):
    """
    Perform database maintenance (for advanced users only)
    """
    if db_path:
        return click.echo(get_db_path())
    elif vacuum:
        get_or_create_db().execute_sql("VACUUM;")
        return click.echo("VACUUM complete.")
    elif truncate:
        if click.confirm("Continue deleting all saved data?") and click.confirm(
            "Are you sure? There's no going back."
        ):
            click.echo("Deleting...")
            Work.truncate_table()
            return click.echo("Deletion successful.")


if __name__ == "__main__":
    main()
