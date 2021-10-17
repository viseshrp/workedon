"""Main module."""
import datetime
import uuid
from pathlib import Path

from platformdirs import user_data_dir
from sqlite_utils import Database

from . import __name__


class DBManager:
    table_name = 'work'
    field_map = {
        "uuid": uuid.UUID,
        "work": str,
        "created": datetime.datetime
    }
    pk_field = "uuid"

    def __init__(self):
        db_file = Path(user_data_dir(__name__, roaming=True)) / "wondb.sqlite"
        # make parent dir.
        db_file.parent.mkdir(parents=True, exist_ok=True)
        self.db_loc = str(db_file.resolve())
        # init db (will create if not found)
        db = Database(self.db_loc)
        # create table if needed
        if not db[self.table_name].exists():
            fields = self.field_map.keys()
            db[self.table_name].create(
                self.field_map,
                pk=self.pk_field,
                not_null=set(fields),
                column_order=list(fields)
            )
        self.table = db[self.table_name]

    def create(self, **kwargs):
        return self.table.insert(kwargs)
