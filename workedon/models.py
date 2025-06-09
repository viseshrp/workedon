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
    FloatField,
    ForeignKeyField,
    Model,
    OperationalError,
    SqliteDatabase,
    TextField,
)
from platformdirs import user_data_dir
from playhouse.migrate import SqliteMigrator, migrate

from .conf import settings
from .constants import APP_NAME, CURRENT_DB_VERSION
from .exceptions import DBInitializationError
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


_db: SqliteDatabase = _get_or_create_db()


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
    duration: FloatField = FloatField(null=True, default=None)

    def __str__(self) -> str:
        """
        Format the object for display.
        Uses a git log like structure.
        """
        if self.uuid is not None:
            user_time = self.timestamp.astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE))
            timestamp_str = user_time.strftime(
                settings.DATETIME_FORMAT or f"{settings.DATE_FORMAT} {settings.TIME_FORMAT}"
            )
            tags = [t.tag.name for t in self.tags.order_by(WorkTag.tag.name)]
            tags_str = f"Tags: {', '.join(tags)}\n" if tags else ""

            if self.duration is not None:
                if settings.DURATION_UNIT in {"h", "hr", "hrs", "hours"}:
                    duration = round(self.duration / 60, 2)
                else:  # default to minutes
                    duration = self.duration
                duration_str = f"Duration: {duration} {settings.DURATION_UNIT}\n"
            else:
                duration_str = ""

            return (
                f'{click.style(f"id: {self.uuid}", fg="green")}\n'
                f'{click.style(f"Date: {timestamp_str}")}\n'
                f"{click.style(tags_str)}"
                f"{click.style(duration_str)}"
                f'\n\t{click.style(self.work, bold=True, fg="white")}\n\n'
            )

        # text-only fallback
        return f'{click.style(f"* {self.work}", bold=True, fg="white")}\n'

    class Meta:
        database: SqliteDatabase = _db
        table_name: str = "work"


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
        database: SqliteDatabase = _db
        table_name: str = "tag"

    def __str__(self) -> str:
        return f'{click.style(f"* {self.name}", fg="white")}\n'


class WorkTag(Model):
    """
    Intermediate model to represent
    many-to-many relationship between
    Work and Tag models.
    """

    work: ForeignKeyField = ForeignKeyField(Work, backref="tags", on_delete="CASCADE")
    tag: ForeignKeyField = ForeignKeyField(Tag, backref="works")

    class Meta:
        database: SqliteDatabase = _db
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


def _create_initial_tables(database: SqliteDatabase) -> None:
    """
    If this is a brand-new database (user_version = 0),
    create all tables (Work, Tag, WorkTag) in one shot.
    Then set user_version = CURRENT_DB_VERSION (3).
    """
    database.create_tables(_models, safe=True)
    _set_db_user_version(database, CURRENT_DB_VERSION)


def _migrate_v1_to_v2(database: SqliteDatabase) -> None:
    """
    Migrate from v1 → v2: create Tag & WorkTag tables.
    Then bump to v2.
    """
    # Create Tag and WorkTag tables
    database.create_tables([Tag, WorkTag], safe=True)
    # Create the duration column in Work table
    migrator = SqliteMigrator(database)
    migrate(migrator.add_column("work", "duration", Work._meta.fields["duration"]))
    # bump the version to 2
    _set_db_user_version(database, 2)


def _apply_pending_migrations(database: SqliteDatabase) -> None:
    """
    Check PRAGMA user_version on the disk.
    - If it's 0, do the initial create (v0 → v2 in one shot).
    - Else if it's 1, run v1 -> v2.
    """
    try:
        existing_version = _get_db_user_version(database)
        # fresh new install
        if existing_version == 0:
            _create_initial_tables(database)
            existing_version = _get_db_user_version(database)
        # v1
        if existing_version < 2:
            _migrate_v1_to_v2(database)
            existing_version = _get_db_user_version(database)
        # Add more future versions here...
        # sanity check
        if existing_version != CURRENT_DB_VERSION:
            msg = (
                f"Database schema mismatch after migration: expected {CURRENT_DB_VERSION},"
                f" found {existing_version}"
            )
            raise DBInitializationError(extra_detail=msg)
    except OperationalError as e:
        raise DBInitializationError(extra_detail=str(e)) from e


@contextlib.contextmanager
def init_db() -> Generator[SqliteDatabase]:
    """
    Context manager to init
    and close the database
    """
    if _db.is_closed():
        _db.connect()
    # set the _db version if not set
    _apply_pending_migrations(_db)
    yield _db
    _db.execute_sql("PRAGMA optimize;")
    _db.close()
