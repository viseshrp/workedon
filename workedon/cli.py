"""Console script for workedon."""
import functools
import warnings

import click
from click_default_group import DefaultGroup

from . import __version__
from .conf import CONF_PATH, settings
from .models import DB_PATH, Work, get_or_create_db
from .utils import load_settings
from .workedon import fetch_work, save_work

warnings.filterwarnings("ignore")
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def settings_options(func):
    @click.option(
        "--date-format",
        "DATE_FORMAT",
        required=False,
        default="",
        type=click.STRING,
        envvar="WORKEDON_DATE_FORMAT",
        help="Sets the date format of the output. Must be a valid Python strftime string.",
    )
    @click.option(
        "--time-format",
        "TIME_FORMAT",
        required=False,
        default="",
        type=click.STRING,
        envvar="WORKEDON_TIME_FORMAT",
        help="Sets the time format of the output. Must be a valid Python strftime string.",
    )
    @click.option(
        "--datetime-format",
        "DATETIME_FORMAT",
        required=False,
        default="",
        type=click.STRING,
        envvar="WORKEDON_DATETIME_FORMAT",
        help="Sets the datetime format of the output. Must be a valid Python strftime string.",
    )
    @click.option(
        "--time-zone",
        "TIME_ZONE",
        required=False,
        default="",
        type=click.STRING,
        envvar="WORKEDON_TIME_ZONE",
        help="Sets the timezone of the output. Must be a valid timezone string.",
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@click.group(
    cls=DefaultGroup,
    context_settings=CONTEXT_SETTINGS,
)
@click.version_option(__version__, "-v", "--version")
def main():
    """
    Work tracking from your shell.

    \b
    Example usages:
    1. Logging work:
    workedon painting the garage
    workedon studying for the SAT @ June 23 2010
    workedon pissing my wife off @ 2pm yesterday

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
@click.option(
    "--print-settings",
    "print_settings",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Print all the current settings, including defaults.",
)
@click.option(
    "--print-settings-path",
    "settings_path",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Print the location of the settings file.",
)
@click.option(
    "--print-db-path",
    "db_path",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Print the location of the database file.",
)
@click.option(
    "--vacuum-db",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Execute the VACUUM command on the database to reclaim some space.",
)
@click.option(
    "--truncate-db",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Delete all data since the beginning of time.",
)
@click.option(
    "--db-version",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Print the version of SQLite being used.",
)
@settings_options
@load_settings
def workedon(
    stuff, settings_path, print_settings, db_path, vacuum_db, truncate_db, db_version, **kwargs
):
    """
    Specify what you worked on, with optional date/time. See examples.

    Options are for advanced users only.
    """
    if settings_path:
        return click.echo(CONF_PATH)
    elif print_settings:
        for key, value in settings.items():
            if key.isupper():
                click.echo(f'{key}="{value}"')
        return
    elif db_path:
        return click.echo(DB_PATH)
    elif vacuum_db:
        click.echo("Performing VACUUM...")
        get_or_create_db().execute_sql("VACUUM;")
        return click.echo("VACUUM complete.")
    elif truncate_db:
        if click.confirm("Continue deleting all saved data? There's no going back."):
            click.echo("Deleting...")
            Work.truncate_table()
            return click.echo("Deletion successful.")
    elif db_version:
        server_version = ".".join([str(num) for num in get_or_create_db().server_version])
        return click.echo(f"SQLite version: {server_version}")
    else:
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
@settings_options
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
    **kwargs,
):
    """
    Fetch and display logged work.

    \b
    If no options are provided, work
    from the past week is returned.
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


if __name__ == "__main__":
    main()
