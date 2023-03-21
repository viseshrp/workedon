# History

## 0.6.2 (2023-03-21)

- more database optimizations
- add --version for the db subcommand to print current SQLite version

## 0.6.1 (2023-03-20)

- add some database optimizations
- add a new "db" subcommand for database maintenance (advanced users only)
- add --print-path to print database file path
- add --vacuum to run VACUUM on the database
- add --truncate to delete all saved work
- Remove usage of reserved keyword "work" and make it available

## 0.6.0 (2023-02-05)

- add fetching by id using --id/-i

## 0.5.9 (2023-02-05)

- make --count work with all other options

## 0.5.8 (2023-01-27)

- fix hash generation

## 0.5.7 (2023-01-26)

- fix deletion

## 0.5.6 (2023-01-25)

- add --since as alternative for --from
- fix formatting in shell

## 0.5.5 (2023-01-23)

- add -l/--text-only for text-only output
- remove -d used as alternative for --delete

## 0.5.4 (2023-01-22)

- add -g as alternative for no-page
- fix help text
- update README
- hashlib: set usedforsecurity

## 0.5.3 (2023-01-18)

- allow reverse sorting using -r/--reverse

## 0.5.2 (2023-01-18)

- remove recording seconds for simple querying
- add --no-page to avoid paging
- improve deleting

## 0.5.1 (2023-01-18)

- fix start \> end check
- add --at to fetch work done at a particular time on a particular
    date/day

## 0.5.0 (2023-01-14)

- Breaking: rename database to won.db

## 0.4.5 (2023-01-13)

- fix error message

## 0.4.4 (2023-01-13)

- raise if start date is greater than end date

## 0.4.3 (2023-01-12)

- don't force color when paging

## 0.4.2 (2023-01-12)

- Python 3.11 support

## 0.4.1 (2023-01-12)

- ask for deletion only if there's something
- use tz aware now() for comparison

## 0.4.0 (2023-01-11)

- Breaking: rename database to wondb.sqlite3
- force colored output on windows
- use tz aware RELATIVE\_BASE

## 0.3.3 (2023-01-09)

- add --delete/-d for deletion
- add --on to fetch work done on a particular date/day
- add --last/-s to fetch the last entered work log

## 0.3.2 (2023-01-08)

- make dependency versions flexible

## 0.3.1 (2023-01-08)

- Fixed README

## 0.3.0 (2023-01-08)

- First release on PyPI.
