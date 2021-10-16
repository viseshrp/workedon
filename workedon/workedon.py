"""Main module."""
import uuid

from .default_settings import DATE_FORMAT, TIME_FORMAT
from .parser import parser


class Work:
    def __init__(self, work, date_time):
        self.id = None  # pk
        self.uuid = uuid.uuid4()
        self.work = work
        self.date_time = date_time

    def save(self):
        print(str(self))

    def __str__(self):
        return f"[{self.date_time.strftime(f'{DATE_FORMAT} {TIME_FORMAT}')}] {self.work}"


def save_work(work):
    work_desc = " ".join(work)
    work, dt = parser.parse(work_desc)
    w = Work(work, dt)
    w.save()
