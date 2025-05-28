from datetime import datetime
from functools import wraps
import hashlib
import uuid

import click

from .conf import settings

import zoneinfo


def get_unique_hash():
    """
    Generate a hash similar to git's commit id
    """
    unique_id = str(uuid.uuid4()).encode("utf-8")
    return hashlib.sha1(unique_id).hexdigest()  # nosec B324


def to_internal_dt(date_time):
    """
    Convert input datetime to internal timezone
    and remove the second and microsecond components.
    """
    return (
        date_time.astimezone(zoneinfo.ZoneInfo(settings.internal_tz))
        .replace(second=0)
        .replace(microsecond=0)
    )


def now():
    """
    Current datetime in user's local timezone
    """
    return datetime.now(zoneinfo.ZoneInfo(settings.TIME_ZONE))


def get_default_time():
    """
    Default internal datetime
    """
    return to_internal_dt(now())


def load_settings(func):
    """
    Loads settings before a
    command is run.
    """

    @wraps(func)
    def handler(*args, **kwargs):
        try:
            from .conf import settings

            user_settings = {}
            for key, value in kwargs.items():
                if key.isupper() and value:
                    user_settings[key] = value
            settings.configure(user_settings=user_settings)

            func(*args, **kwargs)
        except Exception as e:
            raise click.ClickException(click.style(str(e), fg="bright_red"))

    return handler


def add_options(options):
    """
    Add a bunch of click options to a command
    """

    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options
