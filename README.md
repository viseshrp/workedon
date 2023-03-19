workedon
========

[![image](https://img.shields.io/pypi/v/workedon.svg)](https://pypi.python.org/pypi/workedon)
[![Python versions](https://img.shields.io/pypi/pyversions/workedon.svg?logo=python&logoColor=white)](https://pypi.org/project/workedon/)
[![Tests status](https://github.com/viseshrp/workedon/workflows/Test/badge.svg)](https://github.com/viseshrp/workedon/actions?query=workflow%3ATest)
[![Coverage](https://codecov.io/gh/viseshrp/workedon/branch/develop/graph/badge.svg)](https://codecov.io/gh/viseshrp/workedon)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/viseshrp/workedon/blob/develop/LICENSE)
[![Downloads](https://pepy.tech/badge/workedon)](https://pepy.tech/project/workedon)

Work logging from the comfort of your shell.

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

- Log work from your shell in plain text with human-readable dates/times.
  - The date/time is optional. The default is the current date/time.
  - The `@` character is used to separate the text from the
  date/time.
- Fetch logged work with human-readable dates/times.
- Familiar Git-like interface.
- Filter, sort, delete, format and display logged work on your shell.

How it works
------------

This tool is useful in two ways - for logging work and fetching logged work.
The implementation is very simple. Work is logged in the form of
`workedon <text> @ <date>`or just `workedon <text>`
(which uses the current date/time). There is a custom parser that reads the
content, splits it at the `@` to a work and a date component and then uses
the awesome `dateparser` library to parse human-readable dates into datetime
objects. This is then saved in a SQLite database
([File location varies](https://github.com/platformdirs/platformdirs) based
on OS). Logged work can be fetched using multiple options that accept similar
human-readable date/times and uses the same parser to parse and query the
database with datetime objects. The output uses the current shell's pager to
display a paged list similar to `git log`
(your output may vary based on your shell).

Options
--------

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

  Work logging from the comfort of your shell.

  Example usages:
  1. Logging work:
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
  work*  What you worked on, with optional date/time - see examples.
  what   Fetch logged work.

$ workedon what --help
Usage: what [OPTIONS]

  Fetch logged work.

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

- [dateparser](https://github.com/scrapinghub/dateparser), for an
    amazing date parser. This project would not be possible without it.
- [peewee](https://github.com/coleifer/peewee), for a nice and
   tiny ORM to interact with sqlite.
- [Click](https://click.palletsprojects.com), for making writing CLI
    tools a complete pleasure.
- [jrnl](https://github.com/jrnl-org/jrnl),
    [fck](https://github.com/nvbn/thefuck) and
    [Simon Willison](https://github.com/simonw/sqlite-utils/) for some
    inspiration.
