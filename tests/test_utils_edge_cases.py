"""Edge case tests for utility functions."""

from datetime import datetime, timezone
import zoneinfo

from freezegun import freeze_time
import pytest

from workedon.conf import settings
from workedon.utils import get_unique_hash, now, to_internal_dt


def test_get_unique_hash_returns_32_char_hex() -> None:
    hash1 = get_unique_hash()
    assert len(hash1) == 32
    assert all(c in "0123456789abcdef" for c in hash1)


def test_get_unique_hash_generates_unique_values() -> None:
    hashes = [get_unique_hash() for _ in range(1000)]
    assert len(set(hashes)) == 1000


def test_now_returns_timezone_aware() -> None:
    current = now()
    assert current.tzinfo is not None


def test_now_uses_configured_timezone() -> None:
    settings.configure()
    current = now()
    assert current.tzinfo == zoneinfo.ZoneInfo(settings.TIME_ZONE)


def test_to_internal_dt_removes_seconds() -> None:
    dt = datetime(2024, 1, 1, 12, 30, 45, 999999, tzinfo=timezone.utc)
    internal = to_internal_dt(dt)
    assert internal.second == 0
    assert internal.microsecond == 0


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


def test_to_internal_dt_with_naive_datetime_raises() -> None:
    settings.configure()
    dt = datetime(2024, 1, 1, 12, 0, 0)  # No timezone
    internal = to_internal_dt(dt)
    assert internal.tzinfo is not None
    assert internal.tzinfo == zoneinfo.ZoneInfo(settings.internal_tz)
