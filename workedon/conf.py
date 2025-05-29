from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Optional

from platformdirs import user_config_dir

from . import default_settings
from .constants import APP_NAME, SETTINGS_HEADER
from .exceptions import CannotCreateSettingsError, CannotLoadSettingsError

CONF_PATH: Path = Path(user_config_dir(APP_NAME)) / "wonfile.py"


class Settings(dict[str, Any]):
    # lower case settings are internal-only
    # upper case settings are user-configurable

    def __init__(self) -> None:
        super().__init__()
        self.internal_tz: str = "UTC"
        self.internal_dt_format: str = "%Y-%m-%d %H:%M:%S%z"

    def __getattr__(self, item: str) -> Any:
        return self.get(item)

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    def _create_settings_file(self) -> None:
        """
        Create settings file if absent
        """
        # make the parent first
        CONF_PATH.parent.mkdir(parents=True, exist_ok=True)
        # write settings file
        with CONF_PATH.open(mode="w") as settings_file:
            settings_file.write(SETTINGS_HEADER)

    def configure(self, user_settings: Optional[dict[str, Any]] = None) -> None:
        """
        Load or create the user settings file, then populate this Settings dict.
        """
        # create module
        user_settings_module: Any = None

        if not CONF_PATH.is_file():
            try:
                self._create_settings_file()
            except Exception as e:
                raise CannotCreateSettingsError(extra_detail=str(e)) from e
        else:
            # load user settings module
            spec = spec_from_file_location(CONF_PATH.name, CONF_PATH.resolve())
            if spec is None or spec.loader is None:
                raise CannotLoadSettingsError(extra_detail="Bad spec or loader")
            try:
                user_settings_module = module_from_spec(spec)
                spec.loader.exec_module(user_settings_module)
            except Exception as e:
                raise CannotLoadSettingsError(extra_detail=str(e)) from e

        # save to the current object
        for setting in dir(default_settings):
            if setting.isupper():
                # get defaults for fallback
                default = getattr(default_settings, setting)
                self[setting] = getattr(user_settings_module, setting, default)

        # merge settings from current user-options/env vars
        if user_settings:
            self.update(user_settings)


settings: Settings = Settings()
