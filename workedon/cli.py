"""Console script for workedon."""

import click
from click_default_group import DefaultGroup

from . import __version__
from .utils import command_handler
from .workedon import save_work

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
    """CLI Utility for daily work logging"""
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


if __name__ == "__main__":
    main()
