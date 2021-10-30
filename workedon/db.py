"""Main module."""
import datetime
from pathlib import Path

from platformdirs import user_data_dir
from sqlite_utils import Database

from . import __name__


class DBManager:
    TABLE_NAME = 'work'
    FIELD_MAP = {
        "uuid": str,
        "work": str,
        "created": datetime.datetime
    }
    PK_FIELD = "uuid"

    def __init__(self):
        self.db_file = Path(user_data_dir(__name__, roaming=True)) / "wondb.sqlite"
        # init db (will create if not found)
        db = self._get_or_create_db()
        # create table if needed
        if not db[self.TABLE_NAME].exists():
            fields = self.FIELD_MAP.keys()
            db[self.TABLE_NAME].create(
                self.FIELD_MAP,
                pk=self.PK_FIELD,
                not_null=set(fields),
                column_order=list(fields)
            )
        self.table = db[self.TABLE_NAME]

    def _get_or_create_db(self):
        if not self.db_file.is_file():
            # create parent dirs
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
        return Database(self.db_file)

    def create(self, **kwargs):
        self.table.insert(kwargs)
