from datetime import datetime
from functools import wraps
import hashlib
from pathlib import Path
import uuid

import click
from platformdirs import user_data_dir

from . import __name__ as app_name
from .conf import settings

try:
    from backports import zoneinfo
except ImportError:  # pragma: no cover
    import zoneinfo


def get_db_path():
    return Path(user_data_dir(app_name, roaming=True)) / "won.db"


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
    return datetime.now(zoneinfo.ZoneInfo(settings.user_tz))


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

            settings.configure()
            func(*args, **kwargs)
        except Exception as e:
            raise click.ClickException(click.style(str(e), fg="bright_red"))

    return handler
