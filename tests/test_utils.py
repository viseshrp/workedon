from datetime import datetime
import zoneinfo

import click
import pytest

from workedon.conf import settings
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
    assert result.tzinfo.key == "UTC"


def test_now_uses_settings_time_zone(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "TIME_ZONE", "UTC")
    result = now()
    assert result.tzinfo.key == "UTC"


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

    def fake_configure(self, *, user_settings: dict[str, str] | None = None) -> None:
        captured.update(user_settings or {})
        self.update(user_settings or {})

    monkeypatch.setattr(type(settings), "configure", fake_configure)

    @load_settings
    def handler(**kwargs: str) -> str:
        return settings.DATE_FORMAT

    result = handler(DATE_FORMAT="%Y-%m-%d", lower="skip")  # type: ignore[arg-type]
    assert captured == {"DATE_FORMAT": "%Y-%m-%d"}
    assert result == "%Y-%m-%d"


def test_load_settings_wraps_errors_in_click_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(type(settings), "configure", lambda *args, **kwargs: None)

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
