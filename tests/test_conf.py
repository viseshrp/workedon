from pathlib import Path

import pytest

from workedon import conf
from workedon.conf import Settings
from workedon.constants import SETTINGS_HEADER
from workedon.exceptions import CannotCreateSettingsError, CannotLoadSettingsError


def test_settings_getattr_and_setattr() -> None:
    settings = Settings()
    settings.FOO = "bar"
    assert settings.FOO == "bar"
    assert settings["FOO"] == "bar"


def test_configure_creates_settings_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    conf_path = tmp_path / "wonfile.py"
    monkeypatch.setattr(conf, "CONF_PATH", conf_path)

    settings = Settings()
    settings.configure()

    assert conf_path.exists()
    assert SETTINGS_HEADER.strip() in conf_path.read_text()


def test_configure_loads_user_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    conf_path = tmp_path / "wonfile.py"
    conf_path.write_text('TIME_FORMAT = "%H:%M"\n')
    monkeypatch.setattr(conf, "CONF_PATH", conf_path)

    settings = Settings()
    settings.configure()

    assert settings.TIME_FORMAT == "%H:%M"


def test_configure_merges_user_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    conf_path = tmp_path / "wonfile.py"
    conf_path.write_text('DATE_FORMAT = "%Y"\n')
    monkeypatch.setattr(conf, "CONF_PATH", conf_path)

    settings = Settings()
    settings.configure(user_settings={"DATE_FORMAT": "%d"})

    assert settings.DATE_FORMAT == "%d"


def test_configure_raises_on_bad_spec(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    conf_path = tmp_path / "wonfile.py"
    conf_path.write_text("# ok\n")
    monkeypatch.setattr(conf, "CONF_PATH", conf_path)
    monkeypatch.setattr(conf, "spec_from_file_location", lambda *args, **kwargs: None)

    settings = Settings()
    with pytest.raises(CannotLoadSettingsError):
        settings.configure()


def test_configure_raises_on_exec_module_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    conf_path = tmp_path / "wonfile.py"
    conf_path.write_text("raise RuntimeError('boom')\n")
    monkeypatch.setattr(conf, "CONF_PATH", conf_path)

    settings = Settings()
    with pytest.raises(CannotLoadSettingsError) as excinfo:
        settings.configure()
    assert "boom" in str(excinfo.value)


def test_configure_raises_on_settings_file_creation_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    conf_path = tmp_path / "wonfile.py"
    monkeypatch.setattr(conf, "CONF_PATH", conf_path)

    settings = Settings()

    def blow_up() -> None:
        raise OSError("nope")

    monkeypatch.setattr(Settings, "_create_settings_file", blow_up)
    with pytest.raises(CannotCreateSettingsError):
        settings.configure()
