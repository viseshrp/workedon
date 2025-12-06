"""Main module."""

from __future__ import annotations

from collections.abc import Iterator
import datetime
import operator as op
import re
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


def save_work(work: tuple[str, ...], tags_opt: tuple[str, ...], duration_opt: str) -> None:
    """
    Save work from user input
    """
    work_desc = " ".join(work).strip()
    parser = InputParser()
    work_text, dt, duration, tags = parser.parse(work_desc)
    if tags_opt:
        tags.update(set(tags_opt))
    tags = {tag.lower() for tag in tags}

    if duration_opt:
        minutes = parser.parse_duration(f"[{duration_opt.strip()}]")
        if minutes is not None:
            duration = minutes

    data: dict[str, Any] = {
        "work": work_text,
        "timestamp": to_internal_dt(dt),
        "duration": duration,
    }
    try:
        with init_db() as db:
            with db.atomic():
                work_obj = Work.create(**data)
                for tag in tags:
                    tag_obj, _ = Tag.get_or_create(name=tag)
                    WorkTag.create(work=work_obj.uuid, tag=tag_obj.uuid)
            click.echo("Work saved.\n")
            click.echo(work_obj, nl=False)
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
    tags: tuple[str, ...],
    duration: str,
) -> None:
    """
    Fetch saved work filtered based on user input
    """
    # filter fields
    fields = []
    if not delete:
        fields = [Work.work] if text_only else [Work.uuid, Work.timestamp, Work.work, Work.duration]

    # initial set
    work_set = Work.select(*fields)
    # filters
    if work_id:  # id
        work_set = work_set.where(Work.uuid == work_id)
    else:
        # tag
        if tags:
            normalized = [t.lower() for t in tags]
            work_set = work_set.join(WorkTag).join(Tag).where(Tag.name.in_(normalized)).distinct()
        # duration
        if duration:
            # Match optional comparison operator and value (e.g., '>=3h', '<= 45min', '2h')
            match = re.match(r"\s*(==|<=|>=|=|<|>)?\s*(.+)", duration)
            if not match:
                raise CannotFetchWorkError(extra_detail="Invalid duration filter")
            comp_op, dur_str = match.groups()
            comp_op = comp_op or "="
            # Map string operator to Python operator
            op_map = {"=": op.eq, "==": op.eq, ">": op.gt, "<": op.lt, ">=": op.ge, "<=": op.le}
            if comp_op not in op_map:
                raise CannotFetchWorkError(extra_detail=f"Invalid duration operator: {comp_op}")
            minutes = InputParser().parse_duration(f"[{dur_str.strip()}]")
            if minutes is None:
                raise CannotFetchWorkError(extra_detail="Invalid duration value")
            # Work.duration is assumed to be in minutes
            work_set = work_set.where(op_map[comp_op](Work.duration, minutes))
        # date range
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

            if work_count == 0:
                click.echo("Nothing to show, slacker.")
                return

            if work_count == 1 or no_page:
                for work in work_set:
                    click.echo(work, nl=False)
            else:
                gen = work_set.iterator()
                click.echo_via_pager(_generate_work(gen))

    except Exception as e:
        raise CannotFetchWorkError(extra_detail=str(e)) from e


def fetch_tags() -> ModelSelect:
    return Tag.select(Tag.name)
