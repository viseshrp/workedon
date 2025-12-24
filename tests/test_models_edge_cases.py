"""Edge case tests for database models."""

from peewee import IntegrityError
import pytest

from workedon.models import Tag, Work, WorkTag, init_db


def test_work_requires_uuid() -> None:
    with init_db(), pytest.raises(IntegrityError):
        Work.create(uuid=None, work="test")


def test_work_requires_work_text() -> None:
    with init_db(), pytest.raises(IntegrityError):
        Work.create(work=None)


def test_work_allows_null_duration() -> None:
    with init_db():
        work = Work.create(work="test work", duration=None)
        assert work.duration is None


def test_work_allows_zero_duration() -> None:
    with init_db():
        work = Work.create(work="test work", duration=0)
        assert work.duration == 0


def test_work_allows_large_duration() -> None:
    with init_db():
        work = Work.create(work="test work", duration=999999.99)
        assert work.duration == 999999.99


def test_work_string_representation_with_no_tags() -> None:
    with init_db():
        work = Work.create(work="simple work")
        output = str(work)
        assert "simple work" in output
        assert "Tags:" not in output


def test_work_string_representation_with_no_duration() -> None:
    with init_db():
        work = Work.create(work="simple work", duration=None)
        output = str(work)
        assert "Duration:" not in output


def test_tag_requires_unique_name() -> None:
    with init_db():
        Tag.create(name="unique")
        with pytest.raises(IntegrityError):
            Tag.create(name="unique")


def test_tag_allows_empty_string_name() -> None:
    # This might be undesirable but tests current behavior
    with init_db():
        tag = Tag.create(name="")
        assert tag.name == ""


def test_work_tag_cascade_delete() -> None:
    with init_db():
        work = Work.create(work="test work")
        tag = Tag.create(name="test_tag")
        WorkTag.create(work=work, tag=tag)

        # Delete work should cascade to WorkTag
        work.delete_instance()
        assert WorkTag.select().where(WorkTag.work == work.uuid).count() == 0


def test_work_tag_requires_both_keys() -> None:
    with init_db():
        work = Work.create(work="test")
        with pytest.raises((IntegrityError, TypeError)):
            WorkTag.create(work=work)


def test_work_with_very_long_text() -> None:
    with init_db():
        long_text = "a" * 100000
        work = Work.create(work=long_text)
        assert work.work == long_text


def test_work_with_special_characters() -> None:
    with init_db():
        special_text = "Test with 🔥 emoji and\nnewlines\tand\ttabs"
        work = Work.create(work=special_text)
        assert work.work == special_text


def test_multiple_tags_per_work() -> None:
    with init_db():
        work = Work.create(work="test work")
        tags = [Tag.create(name=f"tag{i}") for i in range(10)]

        for tag in tags:
            WorkTag.create(work=work, tag=tag)

        assert len(list(work.tags)) == 10


def test_same_tag_multiple_works() -> None:
    with init_db():
        tag = Tag.create(name="shared")
        works = [Work.create(work=f"work{i}") for i in range(5)]

        for work in works:
            WorkTag.create(work=work, tag=tag)

        assert len(list(tag.works)) == 5
