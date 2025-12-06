from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any
import uuid
import zoneinfo

import click

from .conf import settings


def get_unique_hash() -> str:
    """
    Generate a hash similar to git's commit id.
    """
    return uuid.uuid4().hex


def to_internal_dt(date_time: datetime) -> datetime:
    """
    Convert input datetime to internal timezone
    and remove the second and microsecond components.
    """
    return date_time.astimezone(zoneinfo.ZoneInfo(settings.internal_tz)).replace(
        second=0, microsecond=0
    )


def now() -> datetime:
    """
    Current datetime in user's local timezone.
    """
    return datetime.now(zoneinfo.ZoneInfo(settings.TIME_ZONE))


def get_default_time() -> datetime:
    """
    Default internal datetime.
    """
    return to_internal_dt(now())


def load_settings(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that loads settings before a Click command is run.
    """

    @wraps(func)
    def handler(*args: Any, **kwargs: Any) -> Any:
        try:
            from .conf import settings as _settings

            user_settings: dict[str, Any] = {}
            for key, value in kwargs.items():
                if key.isupper() and value:
                    user_settings[key] = value
            _settings.configure(user_settings=user_settings)

            return func(*args, **kwargs)
        except Exception as e:
            raise click.ClickException(click.style(str(e), fg="bright_red")) from e

    return handler


def add_options(options: list[Callable[..., Any]]) -> Callable[..., Any]:
    """
    Decorator factory that applies each Click option-decorator in `options`.
    """

    def _add_options(func: Callable[..., Any]) -> Callable[..., Any]:
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options
