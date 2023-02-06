workedon
========

[![image](https://img.shields.io/pypi/v/workedon.svg)](https://pypi.python.org/pypi/workedon)
[![Python versions](https://img.shields.io/pypi/pyversions/workedon.svg?logo=python&logoColor=white)](https://pypi.org/project/workedon/)
[![Tests status](https://github.com/viseshrp/workedon/workflows/Test/badge.svg)](https://github.com/viseshrp/workedon/actions?query=workflow%3ATest)
[![Coverage](https://codecov.io/gh/viseshrp/workedon/branch/develop/graph/badge.svg)](https://codecov.io/gh/viseshrp/workedon)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/viseshrp/workedon/blob/develop/LICENSE)
[![Downloads](https://pepy.tech/badge/workedon)](https://pepy.tech/project/workedon)

CLI utility for daily work logging.

![demo](https://raw.githubusercontent.com/viseshrp/workedon/develop/demo.gif)

Installation
------------

``` {.bash}
pip install workedon
```

Requirements
------------

- Python 3.7+

Features
--------

Save by date or fetch work saved by date.

<!-- [[[cog
import cog
from workedon import cli
from click.testing import CliRunner
runner = CliRunner()
result = runner.invoke(cli.main, ["--help"])
out = result.output.replace("Usage: main", "Usage: workedon")
result = runner.invoke(cli.what, ["--help"])
what_out = result.output
cog.out(
    "``` {{.bash}}\n"
    "$ workedon --help\n"
    "{}\n"
    "$ workedon what --help\n"
    "{}\n"
    "```".format(out, what_out)
)
]]] -->
``` {.bash}
$ workedon --help
Usage: workedon [OPTIONS] COMMAND [ARGS]...

  CLI utility for daily work logging.

  Example usages:
  1. Saving work:
  workedon studying for the SAT @ June 2010
  workedon pissing my wife off @ 2pm yesterday
  workedon painting the garage

  2. Fetching work:
  workedon what
  workedon what --from "2pm yesterday" --to "9am today"
  workedon what --today
  workedon what --past-month

Options:
  -v, --version  Show the version and exit.
  -h, --help     Show this message and exit.

Commands:
  work*  Work log with optional date to save - see examples.
  what   Fetch your saved work.

$ workedon what --help
Usage: what [OPTIONS]

  Fetch your saved work.

Options:
  -r, --reverse        Reverse order while sorting.
  -n, --count INTEGER  Number of entries to return.
  -s, --last           Fetch the last thing you worked on
  -i, --id TEXT        id to fetch with.
  -f, --from TEXT      Start date-time to filter with.
  -t, --to TEXT        End date-time to filter with.
  --since TEXT         Fetch work done since a specified date-time in the past.
  -d, --past-day       Fetch work done in the past 24 hours.
  -w, --past-week      Fetch work done in the past week.
  -m, --past-month     Fetch work done in the past month.
  -y, --past-year      Fetch work done in the past year.
  -e, --yesterday      Fetch work done yesterday.
  -o, --today          Fetch work done today.
  --on TEXT            Fetch work done on a particular date/day.
  --at TEXT            Fetch work done at a particular time on a particular
                       date/day.
  --delete             Delete fetched work.
  -g, --no-page        Don't page the output.
  -l, --text-only      Output the work log text only.
  --help               Show this message and exit.

```
<!-- [[[end]]] -->

Credits
-------

- [Click](https://click.palletsprojects.com), for making writing CLI
    tools a complete pleasure.
- [dateparser](https://github.com/scrapinghub/dateparser), for an
    amazing date parser. This project would not be possible without it.
- [jrnl](https://github.com/jrnl-org/jrnl),
    [fck](https://github.com/nvbn/thefuck) and
    [sqlite-utils](https://github.com/simonw/sqlite-utils/) for some
    inspiration.
