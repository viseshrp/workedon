import contextlib
from pathlib import Path

import click
from peewee import (
    CharField,
    CompositeKey,
    DateTimeField,
    ForeignKeyField,
    Model,
    SqliteDatabase,
    TextField,
)
from platformdirs import user_data_dir

from . import __name__ as app_name
from .conf import settings
from .constants import CURRENT_DB_VERSION
from .utils import get_default_time, get_unique_hash

try:
    from backports import zoneinfo
except ImportError:  # pragma: no cover
    import zoneinfo

DB_PATH = Path(user_data_dir(app_name, roaming=True)) / "won.db"


def get_or_create_db():
    """
    Create the database and return the connection
    """
    if not DB_PATH.is_file():
        # create parent dirs
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        DB_PATH.touch()
    return SqliteDatabase(
        str(DB_PATH),
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
            "user_version": CURRENT_DB_VERSION,  # todo: use for migrations
        },
    )


db = get_or_create_db()


class Work(Model):
    """
    Model that represents a Work item
    """

    uuid = CharField(primary_key=True, null=False, default=get_unique_hash)
    created = DateTimeField(
        null=False, formats=[settings.internal_dt_format], default=get_default_time
    )
    work = TextField(null=False)
    timestamp = DateTimeField(
        null=False,
        formats=[settings.internal_dt_format],
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
            user_time = self.timestamp.astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE))
            timestamp = user_time.strftime(
                settings.DATETIME_FORMAT or f"{settings.DATE_FORMAT} {settings.TIME_FORMAT}"
            )
            return (
                f'{click.style(f"id: {self.uuid}", fg="green")}\n'
                f'{click.style(f"Date: {timestamp}")}\n'
                f'\n\t{click.style(f"{self.work}", bold=True, fg="white")}\n\n'
            )
        # text only
        return f'{click.style(f"* {self.work}", bold=True, fg="white")}\n'


class Tag(Model):
    """
    Model that represents a Tag item
    """

    name = CharField(primary_key=True, null=False)

    class Meta:
        database = db
        table_name = "tag"

    def __str__(self):
        return f'{click.style(f"* {self.name}", fg="white")}\n'


class WorkTag(Model):
    """
    Intermediate model to represent
    many-to-many relationship between
    Work and Tag models.
    """

    work = ForeignKeyField(Work, backref="tags")
    tag = ForeignKeyField(Tag, backref="works")

    class Meta:
        database = db
        table_name = "work_tag"
        primary_key = CompositeKey("work", "tag")


_models = [Work, Tag, WorkTag]


@contextlib.contextmanager
def init_db():
    """
    Context manager to init
    and close the database
    """
    if db.is_closed():
        db.connect()
    # creates tables, indexes, sequences
    db.create_tables(_models, safe=True)
    yield db
    db.execute_sql("PRAGMA optimize;")
    db.close()


def truncate_all_tables(**options):
    for model in reversed(_models):
        model.truncate_table(**options)
