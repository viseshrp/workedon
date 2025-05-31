from collections.abc import Generator
import contextlib
from pathlib import Path
from typing import Any
import zoneinfo

import click
from peewee import (
    CharField,
    CompositeKey,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
)
from platformdirs import user_data_dir

from .conf import settings
from .constants import APP_NAME
from .utils import get_default_time, get_unique_hash

DB_PATH: Path = Path(user_data_dir(APP_NAME, roaming=True)) / "won.db"


def _get_or_create_db() -> SqliteDatabase:
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
        },
    )


db: SqliteDatabase = _get_or_create_db()


class Work(Model):
    """
    Model that represents a Work item
    """

    uuid: CharField = CharField(primary_key=True, null=False, default=get_unique_hash)
    created: DateTimeField = DateTimeField(
        null=False, formats=[settings.internal_dt_format], default=get_default_time
    )
    work: TextField = TextField(null=False)
    timestamp: DateTimeField = DateTimeField(
        null=False,
        formats=[settings.internal_dt_format],
        index=True,
        default=get_default_time,
    )
    duration: IntegerField = IntegerField(null=True, default=None)

    class Meta:
        database: SqliteDatabase = db
        table_name: str = "work"

    def __str__(self) -> str:
        """
        Format the object for display.
        Uses a git log like structure.
        """
        if self.timestamp and self.uuid:
            user_time = self.timestamp.astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE))
            timestamp_str = user_time.strftime(
                settings.DATETIME_FORMAT or f"{settings.DATE_FORMAT} {settings.TIME_FORMAT}"
            )
            tags = [t.tag.name for t in self.tags.order_by(WorkTag.tag.name)]
            tags_str = f"Tags: {', '.join(tags)}\n" if tags else ""
            duration_str = f"Duration: {self.duration} mins\n" if self.duration is not None else ""

            return (
                f'{click.style(f"id: {self.uuid}", fg="green")}\n'
                f'{click.style(f"Date: {timestamp_str}")}\n'
                f"{click.style(tags_str)}"
                f"{click.style(duration_str)}"
                f'\t{click.style(self.work, bold=True, fg="white")}\n\n'
            )

        # text-only fallback
        return f'{click.style(f"* {self.work}", bold=True, fg="white")}\n'


class Tag(Model):
    """
    Model that represents a Tag item
    """

    uuid: CharField = CharField(primary_key=True, null=False, default=get_unique_hash)
    name: CharField = CharField(unique=True, null=False)
    created: DateTimeField = DateTimeField(
        null=False, formats=[settings.internal_dt_format], default=get_default_time
    )

    class Meta:
        database: SqliteDatabase = db
        table_name: str = "tag"

    def __str__(self) -> str:
        return f'{click.style(f"* {self.name}", fg="white")}\n'


class WorkTag(Model):
    """
    Intermediate model to represent
    many-to-many relationship between
    Work and Tag models.
    """

    work: ForeignKeyField = ForeignKeyField(Work, backref="tags")
    tag: ForeignKeyField = ForeignKeyField(Tag, backref="works")

    class Meta:
        database: SqliteDatabase = db
        table_name: str = "work_tag"
        primary_key: CompositeKey = CompositeKey("work", "tag")


_models: list[type[Model]] = [Work, Tag, WorkTag]


def truncate_all_tables(**options: dict[str, Any]) -> None:
    for model in reversed(_models):
        model.truncate_table(**options)


def _get_db_user_version(database: SqliteDatabase) -> int:
    """
    Return the current PRAGMA user_version from an open connection.
    """
    cursor = database.execute_sql("PRAGMA user_version;")
    row = cursor.fetchone()
    return row[0] if row else 0


def _set_db_user_version(database: SqliteDatabase, version: int) -> None:
    """
    Set the PRAGMA user_version to the given version.
    """
    database.execute_sql(f"PRAGMA user_version = {version};")


@contextlib.contextmanager
def init_db() -> Generator[SqliteDatabase]:
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
