import contextlib
from pathlib import Path

import click
from peewee import CharField, DateTimeField, Model, SqliteDatabase, TextField
from platformdirs import user_data_dir

from . import __name__ as app_name
from .conf import settings
from .utils import get_default_time, get_unique_hash

try:
    from backports import zoneinfo
except ImportError:  # pragma: no cover
    import zoneinfo


def get_db_path():
    return Path(user_data_dir(app_name, roaming=True)) / "won.db"


def get_or_create_db():
    """
    Create the database and return the connection
    """
    db_file = get_db_path()
    if not db_file.is_file():
        # create parent dirs
        db_file.parent.mkdir(parents=True, exist_ok=True)
        db_file.touch()
    return SqliteDatabase(
        str(db_file),
        pragmas={
            "journal_mode": "wal",  # does not work over a network filesystem.
            "cache_size": -1 * 64000,  # 64MB
            "foreign_keys": 1,
            "ignore_check_constraints": 0,
            "synchronous": "NORMAL",
            "auto_vacuum": "NONE",
            "automatic_index": 1,
            "temp_store": "MEMORY",
            "analysis_limit": 1000,
            "user_version": 1,  # SQLite makes no use of the user-version
        },
    )


db = get_or_create_db()


@contextlib.contextmanager
def init_db():
    """
    Context manager to init
    and close the database
    """
    if db.is_closed():
        db.connect()
    if not Work.table_exists():
        Work.create_table()
    yield
    db.execute_sql("PRAGMA optimize;")
    db.close()


class Work(Model):
    """
    Model that represents a Work item
    """

    uuid = CharField(primary_key=True, null=False, default=get_unique_hash)
    created = DateTimeField(
        null=False, formats=[settings._internal_dt_format], default=get_default_time
    )
    work = TextField(null=False)
    timestamp = DateTimeField(
        null=False,
        formats=[settings._internal_dt_format],
        index=True,
        default=get_default_time,
    )

    class Meta:
        database = db
        table_name = "work"

    def __str__(self):
        """
        Format the object for display.
        Uses a git log like structure.
        """
        if self.timestamp and self.uuid:
            user_time = self.timestamp.astimezone(zoneinfo.ZoneInfo(settings._user_tz))
            timestamp = user_time.strftime(settings.DATETIME_FORMAT)
            return (
                f'{click.style(f"id: {self.uuid}", fg="green")}\n'
                f'{click.style(f"Date: {timestamp}")}\n'
                f'\n\t{click.style(f"{self.work}", bold=True, fg="white")}\n\n'
            )
        else:
            return f'{click.style(f"* {self.work}", bold=True, fg="white")}\n'
