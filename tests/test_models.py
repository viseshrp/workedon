from pathlib import Path

from peewee import OperationalError, SqliteDatabase
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


def test_get_or_create_db_creates_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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


def test_apply_pending_migrations_from_v1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = SqliteDatabase(str(tmp_path / "v1-pending.db"))
    db.connect()
    try:
        db.execute_sql(
            "CREATE TABLE work (uuid TEXT PRIMARY KEY, created DATETIME, work TEXT, timestamp DATETIME);"
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
            "CREATE TABLE work (uuid TEXT PRIMARY KEY, created DATETIME, work TEXT, timestamp DATETIME, duration REAL);"
        )
        db.execute_sql(
            "CREATE TABLE tag (uuid TEXT PRIMARY KEY, name TEXT, created DATETIME);"
        )
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
            "CREATE TABLE work (uuid TEXT PRIMARY KEY, created DATETIME, work TEXT, timestamp DATETIME);"
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
            "CREATE TABLE work (uuid TEXT PRIMARY KEY, created DATETIME, work TEXT, timestamp DATETIME, duration REAL);"
        )
        db.execute_sql(
            "CREATE TABLE tag (uuid TEXT PRIMARY KEY, name TEXT, created DATETIME);"
        )
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
            monkeypatch.setattr(
                models, "get_db_user_version", lambda *_: CURRENT_DB_VERSION + 1
            )
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
            def raise_operational_error(*_args, **_kwargs):
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
