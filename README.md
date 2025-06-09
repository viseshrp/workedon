# workedon

[![PyPI version](https://img.shields.io/pypi/v/workedon.svg)](https://pypi.org/project/workedon/)
[![Python versions](https://img.shields.io/pypi/pyversions/workedon.svg?logo=python&logoColor=white)](https://pypi.org/project/workedon/)
[![CI](https://github.com/viseshrp/workedon/actions/workflows/main.yml/badge.svg)](https://github.com/viseshrp/workedon/actions/workflows/main.yml)
[![Coverage](https://codecov.io/gh/viseshrp/workedon/branch/main/graph/badge.svg)](https://codecov.io/gh/viseshrp/workedon)
[![License: MIT](https://img.shields.io/github/license/viseshrp/workedon)](https://github.com/viseshrp/workedon/blob/main/LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://black.readthedocs.io/en/stable/)
[![Lint: Ruff](https://img.shields.io/badge/lint-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![Typing: mypy](https://img.shields.io/badge/typing-checked-blue.svg)](https://mypy.readthedocs.io/en/stable/)

> Work tracking from your shell.

![Demo](https://raw.githubusercontent.com/viseshrp/workedon/main/demo.gif)

## 🚀 Why this project exists

I believe tracking your work is an important way of measuring productivity
and is a habit that is very helpful to develop. But the thing about habits
is - if they aren’t easy and accessible, you will eventually stop doing
them - just like going to a gym that is 40 minutes away :) I tried
different methods to log my work and failed. Google Docs, iCloud
Notes, Notepad++, Sticky Notes, etc. I really wanted a way of tracking
with very little effort so I could make this a habit.
It's pretty obvious that we all spend most of our day on the terminal.
Wouldn’t it be nice if I wrote a feature, committed it and then logged
what I did right then and there without a second thought?
What if I could also search this based on date so I could look at,
for example, how productive I was in the past week?

`workedon` is another attempt of mine to make work logging a habit and
improve my productivity.

## 🧠 How this project works

This tool is useful in two ways - for logging work and fetching logged work.
The implementation is very simple. Work is logged in the form of
`workedon <text> @ <date>`or just `workedon <text>`
(which uses the current date/time). There is a custom parser that reads the
content, splits it at the `@` to a work and a date component and then uses
the awesome `dateparser` library to parse human-readable dates into datetime
objects. This is then saved in a SQLite database
([File location varies](https://github.com/platformdirs/platformdirs) based
on OS). Logged work can be fetched using multiple options that accept similar
human-readable date/times. The same parser is used again to parse into datetime
objects which are used to query the database. The output uses the current
shell's pager to display a paged list similar to `git log`
(your output may slightly vary based on your shell).

## 📐 Requirements

* Python >= 3.9

## 📦 Installation

```bash
pip install workedon
```

## 🧪 Usage


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
    "{}"
    "```".format(out, what_out)
)
]]] -->
``` {.bash}
$ workedon --help
Usage: workedon [OPTIONS] COMMAND [ARGS]...

  Work tracking from your shell.

  Example usages:
  1. Logging work:
  workedon painting the garage
  workedon studying for the SAT @ June 23 2010
  workedon pissing my wife off @ 2pm yesterday

  2. Fetching work:
  workedon what
  workedon what --from "2pm yesterday" --to "9am today"
  workedon what --today
  workedon what --past-month

Options:
  -v, --version           Show the version and exit.
  --print-settings-path   Print the location of the settings file.
  --print-settings        Print all the current settings, including defaults.
  --list-tags             Print all saved tags.
  --tag TEXT              Tag to add to your work log.
  --duration TEXT         Duration to add to your work log.
  --date-format TEXT      Set the date format of the output. Must be a valid
                          Python strftime string.  [env var:
                          WORKEDON_DATE_FORMAT]
  --time-format TEXT      Set the time format of the output. Must be a valid
                          Python strftime string.  [env var:
                          WORKEDON_TIME_FORMAT]
  --datetime-format TEXT  Set the datetime format of the output. Must be a valid
                          Python strftime string.  [env var:
                          WORKEDON_DATETIME_FORMAT]
  --time-zone TEXT        Set the timezone of the output. Must be a valid
                          timezone string.  [env var: WORKEDON_TIME_ZONE]
  --duration-unit TEXT    Set the unit of the duration output. Must be one of:
                          m/min/mins/minutes or h/hr/hrs/hours. Default is
                          minutes.  [env var: WORKEDON_DURATION_UNIT]
  -h, --help              Show this message and exit.

Commands:
  what  Fetch and display logged work.

$ workedon what --help
Usage: what [OPTIONS]

  Fetch and display logged work.

  If no options are provided, work
  from the past week is returned.

Options:
  -r, --reverse           Reverse order while sorting.
  -n, --count INTEGER     Number of entries to return.
  -s, --last              Fetch the last thing you worked on
  -i, --id TEXT           id to fetch with.
  -f, --from TEXT         Start date-time to filter with.
  -t, --to TEXT           End date-time to filter with.
  --since TEXT            Fetch work done since a specified date-time in the
                          past.
  -d, --past-day          Fetch work done in the past 24 hours.
  -w, --past-week         Fetch work done in the past week.
  -m, --past-month        Fetch work done in the past month.
  -y, --past-year         Fetch work done in the past year.
  -e, --yesterday         Fetch work done yesterday.
  -o, --today             Fetch work done today.
  --on TEXT               Fetch work done on a particular date/day.
  --at TEXT               Fetch work done at a particular time on a particular
                          date/day.
  --delete                Delete fetched work.
  -g, --no-page           Don't page the output.
  -l, --text-only         Output the work log text only.
  --tag TEXT              Tag to filter by. Can be used multiple times to filter
                          by multiple tags.
  --duration TEXT         Duration to filter by.  [default: ""]
  --date-format TEXT      Set the date format of the output. Must be a valid
                          Python strftime string.  [env var:
                          WORKEDON_DATE_FORMAT]
  --time-format TEXT      Set the time format of the output. Must be a valid
                          Python strftime string.  [env var:
                          WORKEDON_TIME_FORMAT]
  --datetime-format TEXT  Set the datetime format of the output. Must be a valid
                          Python strftime string.  [env var:
                          WORKEDON_DATETIME_FORMAT]
  --time-zone TEXT        Set the timezone of the output. Must be a valid
                          timezone string.  [env var: WORKEDON_TIME_ZONE]
  --duration-unit TEXT    Set the unit of the duration output. Must be one of:
                          m/min/mins/minutes or h/hr/hrs/hours. Default is
                          minutes.  [env var: WORKEDON_DURATION_UNIT]
  --help                  Show this message and exit.
```
<!-- [[[end]]] -->

## 🛠️ Features

- Log work from your shell in plain text with human-readable dates/times.
  - The date/time is optional. The default is the current date/time.
  - The `@` character is used to separate the text from the date/time.
- Fetch logged work with human-readable dates/times using multiple options.
- Familiar Git-like interface.
- Filter, sort, delete, format, and display logged work on your shell.
- Set date/time format of the output through settings.
- Specify tags while adding work. Tags can be specified in two ways:
  - The `--tag` option, one or more times for multiple tags. E.g. `--tag tag1 --tag tag2`.
  - The `#` symbol in the description, one or more times. E.g. `#tag1 #tag2`.
    The description must be quoted in this case.
  - Query logged work by tags using the `--tag` option. Using it multiple times will match any
    of the specified tags.
- Specify duration while adding work. Duration can be specified in two ways:
  - The `--duration` option, e.g. `--duration 1h30m` or `--duration 90m`.
  - The `[]` symbol in the description, e.g. `[1.5h]` or `[90m]`.
  - Duration can be specified in hours or minutes.
    - For example, `1h30m` is 1 hour and 30 minutes, and `90m` is also 1 hour and 30 minutes.
  - Duration is case-insensitive and supports `h|hr|hrs|hours|m|min|mins|minutes`.
  - The duration is optional and defaults to an empty string.
  - Only one duration can be specified per log entry.
  - Query logged work by duration using the `--duration` option.

## 🔧 Settings

Whenever `workedon` is run for the first time, a settings file named
`wonfile.py` is generated at the user's configuration directory, which
varies based on OS. To find out, run:

``` {.bash}
workedon --print-settings-path
```

Settings are strings used to configure the behavior of `workedon`.
The currently available settings are:

- `DATE_FORMAT` : Sets the date format of the output.
  - Must be a valid Python [strftime](https://strftime.org/) string.
  - Option: `--date-format <value>`
  - Environment variable: `WORKEDON_DATE_FORMAT`
- `TIME_FORMAT` : Sets the time format of the output.
  - Must be a valid Python [strftime](https://strftime.org/) string.
  - Option: `--time-format <value>`
  - Environment variable: `WORKEDON_TIME_FORMAT`
- `DATETIME_FORMAT` : Sets the date and time format of the output.
  - Must be a valid Python [strftime](https://strftime.org/) string.
  - Setting this overrides `DATE_FORMAT` and `TIME_FORMAT`.
  - Option: `--datetime-format <value>`
  - Environment variable: `WORKEDON_DATETIME_FORMAT`
- `TIME_ZONE` : Sets the time zone of the output.
  - Must be a valid
    [timezone string](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
  - Default is the auto-detected timezone using the
    [tzlocal](https://github.com/regebro/tzlocal) library.
  - Option: `--time-zone <value>`
  - Environment variable: `WORKEDON_TIME_ZONE`

Order of priority is Option > Environment variable > Setting.

To find your current settings, run:

``` {.bash}
workedon --print-settings
```

Check the default settings
[here](https://github.com/viseshrp/workedon/blob/main/workedon/default_settings.py).

## 🧾 Changelog

See [CHANGELOG.md](https://github.com/viseshrp/workedon/blob/main/CHANGELOG.md)

## ⚠️ Limitations

- Your input is limited by your shell. Certain characters like the single
  quote `'` behave differently and `#`. Put your content within double quotes
  to get around special characters.

  For example:

  ``` {.bash}
  workedon "repairing my wife's phone"
  ```

- The [date parser](https://github.com/scrapinghub/dateparser) which is
  used may misinterpret some irregular phrases of date/time, but mostly
  does great.

- `#` and `[]` are reserved characters in the description.
  - `#` is used to specify tags. You can use it multiple times to specify
    multiple tags.
  - `[]` is used to specify duration. You can use it only once per log entry.
  - If you want to use these characters in your description, put your
    description within double quotes.

  For example:

  ``` {.bash}
  workedon "fixing my wife's phone [1h30m] #phone #wife"
  ```

- There are some reserved keywords that are used as subcommands and
  cannot be used as the first word of your log's content:
  - `workedon`
  - `what`

  You can use double quotes here as well to get around this.

  For example, this will not work:

  ``` {.bash}
  workedon what my wife asked me to do @ 3pm 3 days ago
  ```

  This is fine:

  ``` {.bash}
  workedon "what my wife asked me to do" @ 3pm 3 days ago
  ```

## 🙏 Credits

- [dateparser](https://github.com/scrapinghub/dateparser), for an
    amazing date parser. This project would not be possible without it.
- [peewee](https://github.com/coleifer/peewee), for a nice and
   tiny ORM to interact with SQLite.
- [Click](https://click.palletsprojects.com), for making writing CLI
    tools a complete pleasure.
- [jrnl](https://github.com/jrnl-org/jrnl),
    [fck](https://github.com/nvbn/thefuck) and
    [Simon Willison](https://github.com/simonw/sqlite-utils/) for some
    inspiration.

## 📄 License

MIT © [Visesh Prasad](https://github.com/viseshrp)
