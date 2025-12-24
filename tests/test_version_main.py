import importlib
import importlib.metadata
import runpy

import pytest

import workedon
import workedon._version
import workedon.cli


def test_package_exports() -> None:
    assert workedon.__all__ == ["__version__", "main"]
    assert workedon.main is workedon.cli.main
    assert isinstance(workedon.__version__, str)
    assert workedon.__version__


def test_version_fallback_when_package_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_not_found(_name: str) -> str:
        raise importlib.metadata.PackageNotFoundError("workedon")

    monkeypatch.setattr(importlib.metadata, "version", raise_not_found)
    fallback = importlib.reload(workedon._version)
    assert fallback.__version__ == "0.0.0"
    importlib.reload(workedon._version)


def test___main__invokes_cli_main(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"value": False}

    def fake_main() -> None:
        called["value"] = True

    monkeypatch.setattr(workedon.cli, "main", fake_main)
    runpy.run_module("workedon.__main__", run_name="__main__")
    assert called["value"] is True
