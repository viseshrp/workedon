import contextlib
from pathlib import Path

from peewee import Model, CharField, DateTimeField, TextField, SqliteDatabase
from platformdirs import user_data_dir

from .utils import get_unique_hash, now
from . import __name__ as app_name

try:
    from backports import zoneinfo
except ImportError:
    import zoneinfo


def setup_db():
    db_file = Path(user_data_dir(app_name, roaming=True)) / "wondb.sqlite"
    if not db_file.is_file():
        # create parent dirs
        db_file.parent.mkdir(parents=True, exist_ok=True)
        db_file.touch()
    return SqliteDatabase(db_file)


db = setup_db()


@contextlib.contextmanager
def init_db():
    if db.is_closed():
        db.connect()
    if not Work.table_exists():
        Work.create_table()
    yield
    db.close()


class Work(Model):
    uuid = CharField(primary_key=True, null=False, default=get_unique_hash)
    created = DateTimeField(null=False, default=now)
    work = TextField(null=False)
    timestamp = DateTimeField(null=False, index=True)

    class Meta:
        database = db
        table_name = "work"
