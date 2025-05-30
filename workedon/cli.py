"""Console script for workedon."""

from __future__ import annotations

from typing import Any, Callable

import click
from click_default_group import DefaultGroup

from ._version import __version__ as _ver
from .conf import CONF_PATH, settings
from .models import DB_PATH, get_or_create_db, init_db, truncate_all_tables
from .utils import add_options, load_settings
from .workedon import fetch_tags, fetch_work, save_work

CONTEXT_SETTINGS: dict[str, list[str]] = {"help_option_names": ["-h", "--help"]}

# settings
settings_options: list[Callable[..., Any]] = [
    click.option(
        "--date-format",
        "DATE_FORMAT",
        required=False,
        default="",
        type=click.STRING,
        envvar="WORKEDON_DATE_FORMAT",
        show_envvar=True,
        help="Set the date format of the output. Must be a valid Python strftime string.",
    ),
    click.option(
        "--time-format",
        "TIME_FORMAT",
        required=False,
        default="",
        type=click.STRING,
        envvar="WORKEDON_TIME_FORMAT",
        show_envvar=True,
        help="Set the time format of the output. Must be a valid Python strftime string.",
    ),
    click.option(
        "--datetime-format",
        "DATETIME_FORMAT",
        required=False,
        default="",
        type=click.STRING,
        envvar="WORKEDON_DATETIME_FORMAT",
        show_envvar=True,
        help="Set the datetime format of the output. Must be a valid Python strftime string.",
    ),
    click.option(
        "--time-zone",
        "TIME_ZONE",
        required=False,
        default="",
        type=click.STRING,
        envvar="WORKEDON_TIME_ZONE",
        show_envvar=True,
        help="Set the timezone of the output. Must be a valid timezone string.",
    ),
]
# other options
main_options: list[Callable[..., Any]] = [
    click.option(
        "--tag",
        "tags",
        multiple=True,
        required=False,
        type=click.STRING,
        help="Tag to add to your work log.",
    ),
    *settings_options,
]


@click.group(
    cls=DefaultGroup,
    default="workedon",
    default_if_no_args=True,
    context_settings=CONTEXT_SETTINGS,
    invoke_without_command=True,
)
@click.version_option(_ver, "-v", "--version")
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
    "--print-settings",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Print all the current settings, including defaults.",
)
@click.option(
    "--list-tags",
    "list_tags",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    help="Print all saved tags.",
)
@click.option(
    "--db-version",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    hidden=True,
    help="Print the version of SQLite being used.",
)
@click.option(
    "--print-db-path",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    hidden=True,
    help="Print the location of the database file.",
)
@click.option(
    "--vacuum-db",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    hidden=True,
    help="Execute the VACUUM command on the database to reclaim some space.",
)
@click.option(
    "--truncate-db",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
    hidden=True,
    help="Delete all data since the beginning of time.",
)
@add_options(main_options)
@click.pass_context
@load_settings
def main(
    ctx: click.Context,
    settings_path: bool,
    print_settings: bool,
    list_tags: bool,
    db_version: bool,
    print_db_path: bool,
    vacuum_db: bool,
    truncate_db: bool,
    **kwargs: Any,
) -> None:
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
    if ctx.invoked_subcommand:
        return

    if print_db_path:
        click.echo(DB_PATH)
    elif vacuum_db:
        click.echo("Performing VACUUM...")
        with init_db():
            get_or_create_db().execute_sql("VACUUM;")
        click.echo("VACUUM complete.")
    elif truncate_db:
        if click.confirm("Continue deleting all saved data? There's no going back."):
            click.echo("Deleting...")
            with init_db():
                truncate_all_tables()
            click.echo("Deletion successful.")
    elif db_version:
        server_version = ".".join(str(num) for num in get_or_create_db().server_version)
        click.echo(f"SQLite version: {server_version}")
    elif print_settings:
        for key, value in settings.items():
            if key.isupper():
                click.echo(f'{key}="{value}"')
    elif settings_path:
        click.echo(CONF_PATH)
    elif list_tags:
        for tag in fetch_tags():
            click.echo(tag, nl=False)


@main.command(hidden=True)
@click.argument(
    "stuff",
    metavar="<what_you_worked_on>",
    nargs=-1,
    required=False,
    type=click.STRING,
)
@add_options(main_options)
@load_settings
def workedon(stuff: tuple[str, ...], **kwargs: Any) -> None:
    """
    Specify what you worked on, with optional date/time. See workedon --help.
    """
    save_work(stuff, kwargs["tags"])


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
@click.option(
    "--tag",
    required=False,
    default="",
    show_default=True,
    type=click.STRING,
    help="Tag to filter by.",
)
@add_options(settings_options)
@load_settings
def what(
    count: int | None,
    last: bool,
    work_id: str,
    start_date: str,
    end_date: str,
    since: str,
    period: str | None,
    on: str | None,
    at: str | None,
    delete: bool,
    no_page: bool,
    reverse: bool,
    text_only: bool,
    tag: str,
    **kwargs: Any,
) -> None:
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
        tag,
    )


if __name__ == "__main__":
    main()
