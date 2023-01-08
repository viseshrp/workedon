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
    """
    Generate a hash similar to git's commit id
    """
    unique_id = str(uuid.uuid4()).encode("utf-8")
    return hashlib.sha1(unique_id).hexdigest()


def to_internal_dt(date_time):
    """
    Convert input datetime to internal timezone
    and removes microsecond component.
    """
    return date_time.astimezone(zoneinfo.ZoneInfo(settings.internal_tz)).replace(
        microsecond=0
    )


def now():
    """
    Current datetime in user's local timezone
    """
    return datetime.now(zoneinfo.ZoneInfo(settings.user_tz))


def get_default_time():
    """
    Default internal datetime
    """
    return to_internal_dt(now())


def command_handler(func):
    """
    Common decorator that handles
    command runs
    """

    @wraps(func)
    def handle(*args, **kwargs):
        try:
            from .conf import settings

            settings.configure()
            func(*args, **kwargs)
        except Exception as e:
            raise click.ClickException(click.style(str(e), fg="bright_red"))

    return handle
