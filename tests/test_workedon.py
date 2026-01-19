from __future__ import annotations

from collections.abc import Generator, Iterable, Iterator
import contextlib
from datetime import datetime, timedelta
from typing import cast

import click
from freezegun import freeze_time
import pytest

from workedon import workedon
from workedon.conf import settings
from workedon.exceptions import (
    CannotFetchWorkError,
    CannotSaveWorkError,
    StartDateAbsentError,
    StartDateGreaterError,
)
from workedon.models import Tag, Work, WorkTag, init_db


@pytest.fixture(autouse=True)
def configure_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    settings.configure()
    monkeypatch.setattr(settings, "TIME_ZONE", "UTC")
    monkeypatch.setattr(settings, "internal_tz", "UTC")
    monkeypatch.setattr(settings, "DURATION_UNIT", "minutes")


class DummyWork:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value


def test_generate_work_yields_strings() -> None:
    items = [DummyWork("first"), DummyWork("second")]
    work_iter = cast(Iterator[Work], iter(items))
    assert list(workedon._generate_work(work_iter)) == ["first", "second"]


def test_chunked_prefetch_generator_text_only() -> None:
    with init_db():
        Work.create(work="alpha")
        Work.create(work="beta")

        work_set = Work.select(Work.work)
        output = "".join(workedon.chunked_prefetch_generator(work_set, [Work.work], True))

    assert "* alpha" in output
    assert "* beta" in output
    assert "id:" not in output


def test_chunked_prefetch_generator_prefetches_tags() -> None:
    with init_db():
        work = Work.create(work="tagged entry")
        tag = Tag.create(name="tag1")
        WorkTag.create(work=work.uuid, tag=tag.uuid)

        work_set = Work.select(Work.uuid, Work.timestamp, Work.work, Work.duration)
        output = "".join(
            workedon.chunked_prefetch_generator(
                work_set,
                [Work.uuid, Work.timestamp, Work.work, Work.duration],
                False,
            )
        )

    assert "Tags:" in output
    assert "tag1" in output


def test_chunked_prefetch_generator_skips_missing_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with init_db():
        Work.create(work="missing prefetch")
        work_set = Work.select(Work.uuid, Work.timestamp, Work.work, Work.duration)

        monkeypatch.setattr(workedon, "prefetch", lambda *_args, **_kwargs: [])
        output = list(
            workedon.chunked_prefetch_generator(
                work_set,
                [Work.uuid, Work.timestamp, Work.work, Work.duration],
                False,
            )
        )

    assert output == []


def test_get_date_range_requires_start_when_end_provided() -> None:
    with pytest.raises(StartDateAbsentError):
        workedon._get_date_range("", "yesterday", "", None, None, None)


def test_get_date_range_raises_when_start_after_end() -> None:
    with pytest.raises(StartDateGreaterError):
        workedon._get_date_range("yesterday", "2 days ago", "", None, None, None)


def test_get_date_range_at_returns_single_point() -> None:
    start, end = workedon._get_date_range("", "", "", None, None, "3pm yesterday")
    assert start == end


def test_get_date_range_yesterday_period() -> None:
    with freeze_time("2024-01-05 12:00:00"):
        start, end = workedon._get_date_range("", "", "", "yesterday", None, None)
        assert start.date() == datetime(2024, 1, 4).date()
        assert end.date() == datetime(2024, 1, 4).date()
        assert (end - start) >= timedelta(hours=23, minutes=59)


def test_get_date_range_since_uses_now_as_end() -> None:
    with freeze_time("2024-01-05 12:00:00"):
        start, end = workedon._get_date_range("", "", "yesterday", None, None, None)
        assert start.date() == datetime(2024, 1, 4).date()
        assert end.date() == datetime(2024, 1, 5).date()


def test_get_date_range_always_returns_datetime_tuple() -> None:
    """Test that _get_date_range always returns tuple[datetime, datetime] and never None."""
    with freeze_time("2024-01-05 12:00:00"):
        # Test default (no parameters) - should return past week
        start, end = workedon._get_date_range("", "", "", None, None, None)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start < end
        assert (end - start) == timedelta(days=7)


def test_get_date_range_period_today() -> None:
    with freeze_time("2024-01-05 12:00:00"):
        start, end = workedon._get_date_range("", "", "", "today", None, None)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start.date() == datetime(2024, 1, 5).date()
        assert end.date() == datetime(2024, 1, 5).date()


def test_get_date_range_period_day() -> None:
    """Test 'day' period (past 24 hours)."""
    with freeze_time("2024-01-05 12:00:00"):
        start, end = workedon._get_date_range("", "", "", "day", None, None)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start.date() == datetime(2024, 1, 4).date()
        assert end.date() == datetime(2024, 1, 5).date()


def test_get_date_range_period_month() -> None:
    """Test 'month' period (past month)."""
    with freeze_time("2024-01-05 12:00:00"):
        start, end = workedon._get_date_range("", "", "", "month", None, None)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start < end


def test_get_date_range_period_year() -> None:
    """Test 'year' period (past year)."""
    with freeze_time("2024-01-05 12:00:00"):
        start, end = workedon._get_date_range("", "", "", "year", None, None)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start < end


def test_get_date_range_on_parameter() -> None:
    """Test 'on' parameter returns a full day range."""
    with freeze_time("2024-01-05 12:00:00"):
        start, end = workedon._get_date_range("", "", "", None, "yesterday", None)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start.date() == datetime(2024, 1, 4).date()
        # The 'on' parameter sets end to start + 24 hours - 1 second
        assert (end - start) >= timedelta(hours=23, minutes=59)
        assert (end - start) < timedelta(hours=24)


def test_get_date_range_explicit_start_and_end() -> None:
    """Test explicit start_date and end_date parameters."""
    with freeze_time("2024-01-05 12:00:00"):
        start, end = workedon._get_date_range("3 days ago", "yesterday", "", None, None, None)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start < end


def test_get_date_range_explicit_start_only() -> None:
    """Test explicit start_date with default end."""
    with freeze_time("2024-01-05 12:00:00"):
        start, end = workedon._get_date_range("yesterday", "", "", None, None, None)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start < end


def test_save_work_creates_tags_from_option() -> None:
    workedon.save_work(("build", "feature"), ("DevOps",), "")
    with init_db():
        assert Tag.select().where(Tag.name == "devops").exists()
        assert WorkTag.select().count() == 1


def test_save_work_raises_cannot_save_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_error(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(workedon.Work, "create", raise_error)
    with pytest.raises(CannotSaveWorkError) as excinfo:
        workedon.save_work(("fail",), (), "")
    assert "boom" in str(excinfo.value)


def test_fetch_work_raises_cannot_fetch_on_db_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class DBDownError(RuntimeError):
        def __init__(self) -> None:
            super().__init__("db down")

    class BrokenDB:
        def __enter__(self) -> None:
            raise DBDownError()

        def __exit__(self, *_args: object) -> None:
            return None

    monkeypatch.setattr(workedon, "init_db", lambda: BrokenDB())
    with pytest.raises(CannotFetchWorkError) as excinfo:
        workedon.fetch_work(
            count=None,
            work_id="",
            start_date="",
            end_date="",
            since="",
            period=None,
            on=None,
            at=None,
            delete=False,
            no_page=True,
            reverse=False,
            text_only=False,
            tags=(),
            duration="",
        )
    assert "db down" in str(excinfo.value)


def test_fetch_work_delete_declined_keeps_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class DummySelect:
        def where(self, *_args: object, **_kwargs: object) -> DummySelect:
            return self

        def order_by(self, *_args: object, **_kwargs: object) -> DummySelect:
            return self

        def limit(self, *_args: object, **_kwargs: object) -> DummySelect:
            return self

        def exists(self) -> bool:
            return True

    class DummyDelete:
        def where(self, *_args: object, **_kwargs: object) -> DummyDelete:
            return self

        def execute(self) -> int:
            return 0

    deleted = {"called": False}

    def fake_delete() -> DummyDelete:
        deleted["called"] = True
        return DummyDelete()

    @contextlib.contextmanager
    def fake_db() -> Generator[None, None, None]:
        yield None

    def fake_select(*_args: object, **_kwargs: object) -> DummySelect:
        return DummySelect()

    def fake_confirm(*_args: object, **_kwargs: object) -> bool:
        return False

    monkeypatch.setattr(workedon.Work, "select", fake_select)
    monkeypatch.setattr(workedon.Work, "delete", fake_delete)
    monkeypatch.setattr(workedon, "init_db", fake_db)
    monkeypatch.setattr(click, "confirm", fake_confirm)

    workedon.fetch_work(
        count=None,
        work_id="",
        start_date="",
        end_date="",
        since="",
        period=None,
        on=None,
        at=None,
        delete=True,
        no_page=True,
        reverse=False,
        text_only=False,
        tags=(),
        duration="",
    )

    assert deleted["called"] is False


def test_fetch_work_uses_pager_for_multiple_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, list[str]] = {}

    def fake_pager(gen: Iterable[str]) -> None:
        captured["output"] = list(gen)

    class DummySelect:
        def where(self, *_args: object, **_kwargs: object) -> DummySelect:
            return self

        def order_by(self, *_args: object, **_kwargs: object) -> DummySelect:
            return self

        def limit(self, *_args: object, **_kwargs: object) -> DummySelect:
            return self

        def exists(self) -> bool:
            return True

        def count(self) -> int:
            return 2

    @contextlib.contextmanager
    def fake_db() -> Generator[None, None, None]:
        yield None

    def fake_generator(*_args: object, **_kwargs: object) -> Iterator[str]:
        return iter(["id: first\n", "id: second\n"])

    monkeypatch.setattr(click, "echo_via_pager", fake_pager)

    def fake_select(*_args: object, **_kwargs: object) -> DummySelect:
        return DummySelect()

    monkeypatch.setattr(workedon.Work, "select", fake_select)
    monkeypatch.setattr(workedon, "chunked_prefetch_generator", fake_generator)
    monkeypatch.setattr(workedon, "init_db", fake_db)
    workedon.fetch_work(
        count=None,
        work_id="",
        start_date="",
        end_date="",
        since="",
        period=None,
        on=None,
        at=None,
        delete=False,
        no_page=False,
        reverse=False,
        text_only=False,
        tags=(),
        duration="",
    )

    assert any("id:" in line for line in captured.get("output", []))


def test_fetch_tags_returns_saved_tags(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyTag:
        name = "alpha"

    monkeypatch.setattr(workedon.Tag, "select", lambda *_args, **_kwargs: [DummyTag()])
    tags = [tag.name for tag in workedon.fetch_tags()]
    assert tags == ["alpha"]


def test_fetch_work_rejects_invalid_duration_filter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(workedon.re, "match", lambda *_args, **_kwargs: None)
    with pytest.raises(CannotFetchWorkError) as excinfo:
        workedon.fetch_work(
            count=None,
            work_id="",
            start_date="",
            end_date="",
            since="",
            period=None,
            on=None,
            at=None,
            delete=False,
            no_page=True,
            reverse=False,
            text_only=False,
            tags=(),
            duration="n/a",
        )
    assert "Invalid duration filter" in str(excinfo.value)


def test_fetch_work_rejects_invalid_duration_operator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class DummyMatch:
        def groups(self) -> tuple[str, str]:
            return "?!", "5m"

    monkeypatch.setattr(workedon.re, "match", lambda *_args, **_kwargs: DummyMatch())
    with pytest.raises(CannotFetchWorkError) as excinfo:
        workedon.fetch_work(
            count=None,
            work_id="",
            start_date="",
            end_date="",
            since="",
            period=None,
            on=None,
            at=None,
            delete=False,
            no_page=True,
            reverse=False,
            text_only=False,
            tags=(),
            duration="?!5m",
        )
    assert "Invalid duration operator" in str(excinfo.value)
