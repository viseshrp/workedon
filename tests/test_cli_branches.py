import importlib
import os

import pytest

from workedon import cli
import workedon


def test_cli_import_skips_warning_filter_in_debug(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WORKEDON_DEBUG", "1")
    importlib.reload(cli)
    importlib.reload(workedon)
    assert cli.CONTEXT_SETTINGS["help_option_names"] == ["-h", "--help"]
    monkeypatch.delenv("WORKEDON_DEBUG", raising=False)
    importlib.reload(cli)
    importlib.reload(workedon)


def test_main_callback_runs_without_list_tags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli.settings, "configure", lambda *args, **kwargs: None)
    with cli.main.make_context("workedon", []) as ctx:
        ctx.invoked_subcommand = None
        with ctx:
            cli.main.callback(
                settings_path=False,
                print_settings=False,
                list_tags=False,
                db_version=False,
                sqlite_version=False,
                print_db_path=False,
                vacuum_db=False,
                truncate_db=False,
            )
