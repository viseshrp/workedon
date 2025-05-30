"""Main module."""

from __future__ import annotations

from collections.abc import Iterator
import datetime
from typing import Any

import click
from peewee import ModelSelect, chunked

from .constants import WORK_CHUNK_SIZE
from .exceptions import (
    CannotFetchWorkError,
    CannotSaveWorkError,
    StartDateAbsentError,
    StartDateGreaterError,
)
from .models import Tag, Work, WorkTag, init_db
from .parser import InputParser
from .utils import now, to_internal_dt


def save_work(work: tuple[str, ...], tags: tuple[str, ...]) -> None:
    """
    Save work from user input
    """
    work_desc = " ".join(work).strip()
    text, dt, tags_ = InputParser().parse(work_desc)
    if tags:
        tags_.update(set(tags))
    data: dict[str, Any] = {"work": text, "timestamp": to_internal_dt(dt)}
    try:
        with init_db() as db:
            with db.atomic():
                work_ = Work.create(**data)
                for tag in tags_:
                    tag_, _ = Tag.get_or_create(name=tag)
                    WorkTag.create(work=work_.uuid, tag=tag_.name)
            click.echo("Work saved.\n")
            click.echo(work_, nl=False)
    except Exception as e:
        raise CannotSaveWorkError(extra_detail=str(e)) from e


def _generate_work(result: Iterator[Work]) -> Iterator[str]:
    """
    Fetch work in chunks, loop and yield lines of text.
    """
    for work_set in chunked(result, WORK_CHUNK_SIZE):
        for work in work_set:
            yield str(work)


def _get_date_range(
    start_date: str,
    end_date: str,
    since: str,
    period: str | None,
    on: str | None,
    at: str | None,
) -> tuple[datetime.datetime, datetime.datetime]:
    parser = InputParser()
    curr_dt = now()
    # past week is the default
    start = curr_dt - datetime.timedelta(days=7)
    end = curr_dt
    if period:
        if period == "yesterday":
            start = parser.parse_datetime("12am yesterday")
            end = parser.parse_datetime("12am today") - datetime.timedelta(seconds=1)
        elif period == "today":
            start = parser.parse_datetime("12am today")
        elif period == "day":  # past 24 hours
            start = parser.parse_datetime("yesterday")
        elif period == "month":  # past month
            start = parser.parse_datetime("1 month ago")
        elif period == "year":  # past year
            start = parser.parse_datetime("1 year ago")
    elif on:
        start = parser.parse_datetime(on)
        end = start + datetime.timedelta(hours=24) - datetime.timedelta(seconds=1)
    elif at:
        at_time = parser.parse_datetime(at)
        start = at_time
        end = at_time
    elif since:
        start = parser.parse_datetime(since)
    else:
        # need a start to avoid fetching everything since
        # the beginning of time.
        if not start_date and end_date:
            raise StartDateAbsentError
        if start_date:
            start = parser.parse_datetime(start_date)
        if end_date:
            end = parser.parse_datetime(end_date)

    if start > end:
        raise StartDateGreaterError

    return to_internal_dt(start), to_internal_dt(end)


def fetch_work(
    count: int | None,
    work_id: str,
    start_date: str,
    end_date: str,
    since: str,
    period: str | None,
    on: str | None,
    at: str | None,
    delete: bool,
    no_page: bool,
    reverse: bool,
    text_only: bool,
    tag: str,
) -> None:
    """
    Fetch saved work filtered based on user input
    """
    # filter fields
    fields = []
    if not delete:
        fields = [Work.work] if text_only else [Work.uuid, Work.timestamp, Work.work]

    # initial set
    work_set = Work.select(*fields)
    # filters
    if work_id:  # id
        work_set = work_set.where(Work.uuid == work_id)
    else:
        if tag:
            work_set = work_set.join(WorkTag).join(Tag).where(Tag.name == tag)
        # date
        start, end = _get_date_range(start_date, end_date, since, period, on, at)
        if start and end:
            work_set = work_set.where((Work.timestamp >= start) & (Work.timestamp <= end))
        # order
        sort_order = Work.timestamp.asc() if reverse else Work.timestamp.desc()
        work_set = work_set.order_by(sort_order)
        # limit
        if count is not None:
            if count == 0:
                raise CannotFetchWorkError(extra_detail="count must be non-zero")
            work_set = work_set.limit(count)

    # fetch from db now.
    try:
        with init_db():
            work_count = work_set.count()
            if delete:
                if work_count > 0 and click.confirm(f"Continue deleting {work_count} log(s)?"):
                    click.echo("Deleting...")
                    deleted = Work.delete().where(Work.uuid.in_(work_set)).execute()
                    click.echo(f"{deleted} log(s) deleted successfully.")
                elif work_count == 0:
                    click.echo("Nothing to delete.")
                return

            if work_count == 1:
                click.echo(work_set[0], nl=False)
            elif work_count > 1:
                if no_page:
                    for work in work_set:
                        click.echo(work, nl=False)
                else:
                    gen = work_set.iterator()
                    click.echo_via_pager(_generate_work(gen))
            else:
                click.echo("Nothing to show, slacker.")
    except Exception as e:
        raise CannotFetchWorkError(extra_detail=str(e)) from e


def fetch_tags() -> ModelSelect:
    return Tag.select(Tag.name)
