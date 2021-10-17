"""Main module."""
import uuid

from .db import DBManager
from .exceptions import CannotSaveWorkError
from .parser import parser
from .utils import pretty_print_work


class Work:
    db = DBManager()

    def __init__(self, work, created):
        self.uuid = str(uuid.uuid4())
        self.work = work
        self.created = created

    def save(self):
        try:
            self.db.create(uuid=self.uuid, work=self.work, created=self.created)
        except Exception as e:
            raise CannotSaveWorkError(extra_detail=str(e))


@pretty_print_work
def save_work(work):
    work_desc = " ".join(work)
    text, dt = parser.parse(work_desc)
    w = Work(text, dt)
    w.save()
    return w
