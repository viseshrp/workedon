from collections.abc import Generator
import contextlib

import pytest

from workedon.models import DB_PATH


@pytest.fixture(autouse=True, scope="function")
def cleanup() -> Generator[None, None, None]:
    yield
    # delete db after every test
    with contextlib.suppress(FileNotFoundError):
        DB_PATH.unlink()
