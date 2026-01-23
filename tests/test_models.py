from pathlib import Path

from peewee import IntegrityError, OperationalError, SqliteDatabase
import pytest

from workedon import models
from workedon.conf import settings
from workedon.constants import CURRENT_DB_VERSION
from workedon.exceptions import DBInitializationError
from workedon.models import Tag, Work, WorkTag, init_db


@pytest.fixture(autouse=True)
def configure_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    settings.configure()
    monkeypatch.setattr(settings, "TIME_ZONE", "UTC")
    monkeypatch.setattr(settings, "internal_tz", "UTC")


def test_get_or_create_db_creates_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "won.db"
    monkeypatch.setattr(models, "DB_PATH", db_path)

    db = models._get_or_create_db()
    try:
        assert db_path.exists()
        assert db.database == str(db_path)
    finally:
        db.close()


def test_get_or_create_db_uses_existing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "won.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.write_text("")
    monkeypatch.setattr(models, "DB_PATH", db_path)

    db = models._get_or_create_db()
    try:
        assert db_path.exists()
        assert db.database == str(db_path)
    finally:
        db.close()


def test_get_and_set_db_user_version(tmp_path: Path) -> None:
    db = SqliteDatabase(str(tmp_path / "version.db"))
    db.connect()
    try:
        models._set_db_user_version(db, 5)
        assert models.get_db_user_version(db) == 5
    finally:
        db.close()


def test_apply_pending_migrations_from_zero(tmp_path: Path) -> None:
    db = SqliteDatabase(str(tmp_path / "fresh.db"))
    db.connect()
    try:
        with db.bind_ctx([Work, Tag, WorkTag]):
            models._apply_pending_migrations(db)
            assert models.get_db_user_version(db) == CURRENT_DB_VERSION
            assert {"work", "tag", "work_tag"}.issubset(set(db.get_tables()))
    finally:
        db.close()


def test_apply_pending_migrations_from_v1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = SqliteDatabase(str(tmp_path / "v1-pending.db"))
    db.connect()
    try:
        db.execute_sql(
            "CREATE TABLE work (uuid TEXT PRIMARY KEY, created DATETIME, work TEXT, "
            "timestamp DATETIME);"
        )
        models._set_db_user_version(db, 1)

        def fake_migrate_v2_to_v3(database: SqliteDatabase) -> None:
            models._set_db_user_version(database, CURRENT_DB_VERSION)

        monkeypatch.setattr(models, "_migrate_v2_to_v3", fake_migrate_v2_to_v3)
        with db.bind_ctx([Work, Tag, WorkTag]):
            models._apply_pending_migrations(db)

        assert models.get_db_user_version(db) == CURRENT_DB_VERSION
        cols = [row[1] for row in db.execute_sql("PRAGMA table_info(work);").fetchall()]
        assert "duration" in cols
        assert {"tag", "work_tag"}.issubset(set(db.get_tables()))
    finally:
        db.close()


def test_apply_pending_migrations_from_v2(tmp_path: Path) -> None:
    db = SqliteDatabase(str(tmp_path / "v2-pending.db"))
    db.connect()
    try:
        db.execute_sql(
            "CREATE TABLE work (uuid TEXT PRIMARY KEY, created DATETIME, work TEXT, "
            "timestamp DATETIME, duration REAL);"
        )
        db.execute_sql("CREATE TABLE tag (uuid TEXT PRIMARY KEY, name TEXT, created DATETIME);")
        db.execute_sql("CREATE TABLE work_tag (work TEXT, tag TEXT);")
        models._set_db_user_version(db, 2)
        with db.bind_ctx([Work, Tag, WorkTag]):
            models._apply_pending_migrations(db)

        assert models.get_db_user_version(db) == CURRENT_DB_VERSION
        indexes = [row[1] for row in db.execute_sql("PRAGMA index_list(work);").fetchall()]
        assert any("duration" in name for name in indexes)
    finally:
        db.close()


def test_migrate_v1_to_v2_adds_tables_and_duration(tmp_path: Path) -> None:
    db = SqliteDatabase(str(tmp_path / "v1.db"))
    db.connect()
    try:
        db.execute_sql(
            "CREATE TABLE work (uuid TEXT PRIMARY KEY, created DATETIME, work TEXT, "
            "timestamp DATETIME);"
        )
        models._set_db_user_version(db, 1)
        with db.bind_ctx([Work, Tag, WorkTag]):
            models._migrate_v1_to_v2(db)

        assert models.get_db_user_version(db) == 2
        assert {"tag", "work_tag"}.issubset(set(db.get_tables()))
        cols = [row[1] for row in db.execute_sql("PRAGMA table_info(work);").fetchall()]
        assert "duration" in cols
    finally:
        db.close()


def test_migrate_v2_to_v3_adds_duration_index(tmp_path: Path) -> None:
    db = SqliteDatabase(str(tmp_path / "v2.db"))
    db.connect()
    try:
        db.execute_sql(
            "CREATE TABLE work (uuid TEXT PRIMARY KEY, created DATETIME, work TEXT, "
            "timestamp DATETIME, duration REAL);"
        )
        db.execute_sql("CREATE TABLE tag (uuid TEXT PRIMARY KEY, name TEXT, created DATETIME);")
        db.execute_sql("CREATE TABLE work_tag (work TEXT, tag TEXT);")
        models._set_db_user_version(db, 2)
        with db.bind_ctx([Work, Tag, WorkTag]):
            models._migrate_v2_to_v3(db)

        assert models.get_db_user_version(db) == CURRENT_DB_VERSION
        indexes = [row[1] for row in db.execute_sql("PRAGMA index_list(work);").fetchall()]
        assert any("duration" in name for name in indexes)
    finally:
        db.close()


def test_apply_pending_migrations_raises_on_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = SqliteDatabase(str(tmp_path / "bad.db"))
    db.connect()
    try:
        with db.bind_ctx([Work, Tag, WorkTag]):
            monkeypatch.setattr(models, "get_db_user_version", lambda *_: CURRENT_DB_VERSION + 1)
            with pytest.raises(DBInitializationError):
                models._apply_pending_migrations(db)
    finally:
        db.close()


def test_apply_pending_migrations_wraps_operational_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = SqliteDatabase(str(tmp_path / "bad-op.db"))
    db.connect()
    try:
        with db.bind_ctx([Work, Tag, WorkTag]):

            def raise_operational_error(*_args: object, **_kwargs: object) -> None:
                raise OperationalError("fail")

            monkeypatch.setattr(db, "execute_sql", raise_operational_error)
            with pytest.raises(DBInitializationError) as excinfo:
                models._apply_pending_migrations(db)
            assert "fail" in str(excinfo.value)
    finally:
        db.close()


def test_truncate_all_tables_clears_rows() -> None:
    with init_db():
        work = Work.create(work="cleanup test")
        tag = Tag.create(name="cleanup")
        WorkTag.create(work=work.uuid, tag=tag.uuid)

        models.truncate_all_tables()

        assert Work.select().count() == 0
        assert Tag.select().count() == 0
        assert WorkTag.select().count() == 0


def test_tag_str_and_work_text_only_str() -> None:
    tag = Tag(name="alpha")
    assert "* alpha" in str(tag)

    work = Work(uuid=None, work="text only")
    assert "* text only" in str(work)


# ---edge-cases---


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


def test_tag_rejects_empty_string_name() -> None:
    with init_db(), pytest.raises(IntegrityError):
        Tag.create(name="")


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
        special_text = "Test with symbols !@# and\nnewlines\tand\ttabs"
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
