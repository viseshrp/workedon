# -*- coding: utf-8 -*-

"""Console script for workedon."""
# enable absolute imports of this module for Python2.x
from __future__ import absolute_import
from __future__ import unicode_literals  # unicode support for py2

import click

from . import __version__
from .workedon import run

click.disable_unicode_literals_warning = True


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(__version__, '-v', '--version')
@click.argument('myarg')
def main(myarg):
    """
    CLI tool for daily work logging

    Example usages:

    $ workedon --help

    """
    try:
        run(myarg)
    except Exception as e:
        # all other exceptions
        raise click.ClickException(e)


if __name__ == "__main__":
    main()  # pragma: no cover
