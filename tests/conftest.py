from collections.abc import Generator
import contextlib
import logging
from pathlib import Path

import pytest

from workedon.models import DB_PATH


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
