import hashlib
import uuid
from datetime import datetime
from functools import wraps

import click

from .conf import settings

try:
    from backports import zoneinfo
except ImportError:
    import zoneinfo


def get_unique_hash():
    unique_id = str(uuid.uuid4()).encode('utf-8')
    return hashlib.sha1(unique_id).hexdigest()


def to_internal_tz(date_time):
    return date_time.astimezone(zoneinfo.ZoneInfo(settings.internal_tz))


def now():
    user_time = datetime.now(zoneinfo.ZoneInfo(settings.user_tz))
    return to_internal_tz(user_time)


def command_handler(func):
    @wraps(func)
    def handle(*args, **kwargs):
        try:
            from .conf import settings
            settings.configure()
            func(*args, **kwargs)
        except Exception as e:
            raise click.ClickException(click.style(str(e), fg='bright_red'))

    return handle
