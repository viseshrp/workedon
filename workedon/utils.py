import hashlib
import sys
import uuid
from functools import wraps

import click

from .conf import settings

if sys.version_info >= (3, 9):
    import zoneinfo
else:
    from backports import zoneinfo


def to_internal_tz(date_time):
    return date_time.astimezone(zoneinfo.ZoneInfo(settings.internal_tz))


def get_unique_hash():
    unique_id = str(uuid.uuid4()).encode('utf-8')
    return hashlib.sha1(unique_id).hexdigest()


def click_handler(func):
    @wraps(func)
    def handle(*args, **kwargs):
        try:
            from .conf import settings
            settings.configure()
            func(*args, **kwargs)
        except Exception as e:
            raise click.ClickException(click.style(str(e), fg='bright_red'))

    return handle
