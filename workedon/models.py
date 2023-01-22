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
except ImportError:
    import zoneinfo


def create_db():
    """
    Create the database and return the connection
    """
    db_file = Path(user_data_dir(app_name, roaming=True)) / "won.db"
    if not db_file.is_file():
        # create parent dirs
        db_file.parent.mkdir(parents=True, exist_ok=True)
        db_file.touch()
    return SqliteDatabase(str(db_file))


db = create_db()


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
    db.close()


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
        user_time = self.timestamp.astimezone(zoneinfo.ZoneInfo(settings.user_tz))
        time = user_time.strftime(settings.DATETIME_FORMAT)
        return (
            f'\n{click.style(f"id: {self.uuid}", fg="green")}'
            f'\n{click.style(f"Date: {time}")}'
            f'\n\n\t{click.style(f"{self.work}", bold=True, fg="white")}\n'
        )
