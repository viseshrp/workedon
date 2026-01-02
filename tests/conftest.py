from collections.abc import Generator
import contextlib
from datetime import datetime
import logging
from pathlib import Path

from click.testing import CliRunner
from freezegun import freeze_time
import pytest

from workedon.models import DB_PATH


@pytest.fixture
def runner() -> CliRunner:
    """Provides a Click CLI runner."""
    return CliRunner()


@pytest.fixture(autouse=True, scope="session")
def freeze_clock_at_2359() -> Generator[None, None, None]:
    """
    Freeze every test at a fixed date (23:59:00) so relative date parsing
    (“yesterday”, “tomorrow”, etc.) is deterministic across runs.
    """
    target = datetime(2024, 1, 10, 23, 59, 0)
    with freeze_time(target):
        yield


def safe_unlink(path: Path) -> None:
    try:
        path.unlink()
    except PermissionError:
        # Windows workaround: try to mark for deletion later
        import gc

        gc.collect()
        try:
            path.unlink()
        except Exception:
            logging.exception(f"Failed to delete {path}. It may be in use by another process.")


@pytest.fixture(autouse=True, scope="function")
def cleanup() -> Generator[None, None, None]:
    yield
    # delete db after every test
    with contextlib.suppress(FileNotFoundError):
        safe_unlink(DB_PATH)
