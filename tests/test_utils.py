from datetime import datetime, timezone
from typing import cast
import zoneinfo

import click
from freezegun import freeze_time
import pytest

from workedon.conf import Settings, settings
from workedon.utils import (
    add_options,
    get_default_time,
    get_unique_hash,
    load_settings,
    now,
    to_internal_dt,
)


def test_get_unique_hash_is_hex_and_unique() -> None:
    first = get_unique_hash()
    second = get_unique_hash()
    assert first != second
    assert len(first) == 32
    int(first, 16)


def test_to_internal_dt_trims_seconds_and_uses_internal_tz(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "internal_tz", "UTC")
    dt = datetime(2024, 1, 1, 12, 34, 56, 123456, tzinfo=zoneinfo.ZoneInfo("UTC"))
    result = to_internal_dt(dt)
    assert result.second == 0
    assert result.microsecond == 0
    tzinfo = result.tzinfo
    assert isinstance(tzinfo, zoneinfo.ZoneInfo)
    assert tzinfo.key == "UTC"


def test_now_uses_settings_time_zone(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "TIME_ZONE", "UTC")
    result = now()
    tzinfo = result.tzinfo
    assert isinstance(tzinfo, zoneinfo.ZoneInfo)
    assert tzinfo.key == "UTC"


def test_get_default_time_matches_to_internal_dt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "internal_tz", "UTC")
    monkeypatch.setattr(settings, "TIME_ZONE", "UTC")
    result = get_default_time()
    assert result.second == 0
    assert result.microsecond == 0


def test_load_settings_merges_uppercase_kwargs(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, str] = {}

    def fake_configure(self: Settings, *, user_settings: dict[str, str] | None = None) -> None:
        captured.update(user_settings or {})
        self.update(user_settings or {})

    monkeypatch.setattr(type(settings), "configure", fake_configure)

    @load_settings
    def handler(**kwargs: str) -> str:
        return cast(str, settings.DATE_FORMAT)

    result = handler(DATE_FORMAT="%Y-%m-%d", lower="skip")
    assert captured == {"DATE_FORMAT": "%Y-%m-%d"}
    assert result == "%Y-%m-%d"


def test_load_settings_wraps_errors_in_click_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def noop_configure(*_args: object, **_kwargs: object) -> None:
        return None

    monkeypatch.setattr(type(settings), "configure", noop_configure)

    @load_settings
    def handler() -> None:
        raise ValueError("boom")

    with pytest.raises(click.ClickException) as excinfo:
        handler()
    assert "boom" in str(excinfo.value)


def test_add_options_applies_click_options() -> None:
    options = [
        click.option("--alpha", is_flag=True, default=False),
        click.option("--beta", type=click.INT, default=1),
    ]

    @add_options(options)
    def handler() -> None:
        return None

    assert hasattr(handler, "__click_params__")
    assert {param.name for param in handler.__click_params__} == {"alpha", "beta"}


# ---edge-cases---


def test_now_returns_timezone_aware() -> None:
    settings.configure()
    current = now()
    assert current.tzinfo is not None


def test_to_internal_dt_converts_timezone() -> None:
    settings.configure()
    dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    internal = to_internal_dt(dt)
    assert internal.tzinfo == zoneinfo.ZoneInfo(settings.internal_tz)


def test_to_internal_dt_preserves_date() -> None:
    dt = datetime(2024, 6, 15, 23, 59, 59, tzinfo=timezone.utc)
    internal = to_internal_dt(dt)
    # Date might shift due to timezone conversion
    assert abs((internal.date() - dt.date()).days) <= 1


def test_now_frozen_time(monkeypatch: pytest.MonkeyPatch) -> None:
    settings.configure()
    monkeypatch.setattr(settings, "TIME_ZONE", "UTC")
    with freeze_time("2024-01-15 12:00:00"):
        current = now()
        assert current.hour == 12
        assert current.minute == 0


def test_to_internal_dt_sets_internal_timezone_for_naive_datetime() -> None:
    settings.configure()
    dt = datetime(2024, 1, 1, 12, 0, 0)  # No timezone
    internal = to_internal_dt(dt)
    assert internal.tzinfo is not None
    assert internal.tzinfo == zoneinfo.ZoneInfo(settings.internal_tz)
