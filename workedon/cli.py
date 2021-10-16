"""Console script for workedon."""

import click

from . import __version__
from .workedon import save_work


@click.command(
    options_metavar="<options>",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.version_option(
    __version__,
    "-v",
    "--version"
)
@click.argument(
    "work",
    metavar="<what_you_worked_on>",
    nargs=-1,
    required=True,
    type=click.STRING
)
def main(work):
    """Console script for workedon."""
    try:
        if work:
            from .conf import settings
            settings.configure()
            # save
            save_work(work)
    except Exception as e:
        raise click.ClickException(str(e))


if __name__ == "__main__":
    main()
