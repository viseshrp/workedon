"""Console script for workedon."""
import sys

import click

from . import __version__


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(__version__, "-v", "--version")
def main(args=None):
    """Console script for workedon."""
    click.echo("Replace this message by putting your code into " "workedon.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
