from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from platformdirs import user_config_dir
from tzlocal import get_localzone

from . import __name__, default_settings
from .constants import SETTINGS_HEADER
from .exceptions import CannotCreateSettingsError, CannotLoadSettingsError

CONF_PATH = Path(user_config_dir(__name__)) / "wonfile.py"


class Settings(dict):
    # lower case settings are internal-only
    # upper case settings are user-configurable
    def __init__(self):
        super().__init__()
        self.internal_tz = "UTC"  # for internal storage and manipulation
        self.internal_dt_format = "%Y-%m-%d %H:%M:%S%z"

    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, key, value):
        self[key] = value

    def _create_settings_file(self):
        """
        Create settings file if absent
        """
        # make the parent first
        CONF_PATH.parent.mkdir(parents=True, exist_ok=True)
        # write settings file
        with CONF_PATH.open(mode="w") as settings_file:
            settings_file.write(SETTINGS_HEADER)

    def configure(self, user_settings=None):
        """
        Configuration
        """
        user_settings_module = None
        # create module
        if not CONF_PATH.is_file():
            try:
                self._create_settings_file()
            except Exception as e:
                raise CannotCreateSettingsError(extra_detail=str(e))
        else:
            # load user settings module
            try:
                spec = spec_from_file_location(CONF_PATH.name, CONF_PATH.resolve())
                user_settings_module = module_from_spec(spec)
                spec.loader.exec_module(user_settings_module)
            except Exception as e:
                raise CannotLoadSettingsError(extra_detail=str(e))

        # save to the current object
        for setting in dir(default_settings):
            if setting.isupper():
                # get defaults for fallback
                default = getattr(default_settings, setting)
                self[setting] = getattr(user_settings_module, setting, default)

        # merge settings from current user-options/env vars
        if user_settings:
            self.update(user_settings)


settings = Settings()
