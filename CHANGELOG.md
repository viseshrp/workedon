# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - [Unreleased]

### Added

- Allow specifying tags while adding work. Tags can be specified in 2 ways:
  - The `--tag` option, one or more times for multiple tags. E.g. `--tag tag1 --tag tag2`.
  - The `#` symbol in the description, one or more times. E.g. `#tag1 #tag2`.
  The description must be quoted in this case.
  - Tags are case-sensitive.
- Querying by tags using the `--tag` option. Using multiple times will match any of the specified tags.
- Specifying duration while adding work.
  - The `--duration` option, e.g. `--duration 1h30m` or `--duration 90m`.
  - The `[]` symbol in the description, e.g. `[1.5h]` or `[90m]`. The description must be quoted in this case.
  - Duration is case-insensitive. Allows `h|hr|hrs|hours|m|min|mins|minutes`.
- Querying by duration using the `--duration` option.

### Changed

- Switched from `hashlib.sha1` to UUID-based identifiers without hashing
- Modernized the codebase.
- Updated dependencies to their latest versions

### Fixed

- Handling of empty datetime inputs

### Removed

- Unused imports and redundant logic
- Obsolete zoneinfo fallback

## [0.7.0] - 2023-04-07

### Added

- Option and environment variable alternatives for all settings
- Setting to specify timezone for display
  - Setting: `TIME_ZONE`
  - Option: `--time-zone <value>`
  - Env var: `WORKEDON_TIME_ZONE`

### Changed

- Usage of date/time formatting settings

### Removed

- ⚠️ **Breaking** (for advanced users only): Removed `db` and `conf` subcommands
  - `workedon db --print-path` → `workedon --print-db-path`
  - `workedon db --vacuum` → `workedon --vacuum-db`
  - `workedon db --truncate` → `workedon --truncate-db`
  - `workedon db --version` → `workedon --db-version`
  - `workedon conf --print-path` → `workedon --print-settings-path`
  - `workedon conf --print` → `workedon --print-settings`
  - All these options are now hidden from the help output

## [0.6.3] - 2023-04-02

### Added

- Enable settings file `wonfile.py`
- Settings: `DATE_FORMAT`, `TIME_FORMAT`, `DATETIME_FORMAT`
- `conf` command to view settings

### Fixed

- `load_module` deprecation
- Default date/time format

## [0.6.2] - 2023-03-21

### Added

- `--version` for the `db` subcommand to print current SQLite version

### Changed

- More database optimizations

## [0.6.1] - 2023-03-20

### Added

- Database optimizations
- New `db` subcommand for maintenance
- `--print-path` to print database file path
- `--vacuum` to run VACUUM
- `--truncate` to delete all saved work

### Changed

- Freed up reserved keyword `work`

## [0.6.0] - 2023-02-05

### Added

- Fetching by ID with `--id` / `-i`

## [0.5.9] - 2023-02-05

### Changed

- `--count` works with all other options

## [0.5.8] - 2023-01-27

### Fixed

- Hash generation

## [0.5.7] - 2023-01-26

### Fixed

- Deletion behavior

## [0.5.6] - 2023-01-25

### Added

- `--since` as alternative for `--from`

### Fixed

- Shell formatting

## [0.5.5] - 2023-01-23

### Added

- `-l` / `--text-only` for text-only output

### Removed

- `-d` as alias for `--delete`

## [0.5.4] - 2023-01-22

### Added

- `-g` as alternative for `--no-page`

### Fixed

- Help text
- README update
- `usedforsecurity` in `hashlib`

## [0.5.3] - 2023-01-18

### Added

- Reverse sorting with `-r` / `--reverse`

## [0.5.2] - 2023-01-18

### Added

- `--no-page` to avoid paging

### Changed

- Removed seconds in timestamps for simpler querying
- Improved deletion

## [0.5.1] - 2023-01-18

### Added

- `--at` to fetch work done at a specific time and date

### Fixed

- Validation for `start > end`

## [0.5.0] - 2023-01-14

### Changed

- ⚠️ Breaking: Rename database file to `won.db`
  (New DB will be created; old one becomes obsolete)

## [0.4.5] - 2023-01-13

### Fixed

- Error messages

## [0.4.4] - 2023-01-13

### Fixed

- Raise error if start date is after end date

## [0.4.3] - 2023-01-12

### Fixed

- No forced color when paging

## [0.4.2] - 2023-01-12

### Added

- Python 3.11 support

## [0.4.1] - 2023-01-12

### Changed

- Ask for deletion only if there's data
- Use timezone-aware `now()` for comparisons

## [0.4.0] - 2023-01-11

### Changed

- ⚠️ Breaking: Rename DB to `wondb.sqlite3`
- Force colored output on Windows
- Use timezone-aware `RELATIVE_BASE`

## [0.3.3] - 2023-01-09

### Added

- `--delete` / `-d` for deletion
- `--on` for filtering by date
- `--last` / `-s` to show last work log

## [0.3.2] - 2023-01-08

### Changed

- Made dependency versions flexible

## [0.3.1] - 2023-01-08

### Fixed

- README content

## [0.3.0] - 2023-01-08

### Added

- First PyPI release

## [0.0.1] - 2022-01-01

### Added

- Stub release
