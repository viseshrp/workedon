from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from platformdirs import user_config_dir
from tzlocal import get_localzone

from . import __name__, default_settings
from .constants import SETTINGS_HEADER
from .exceptions import CannotCreateSettingsError, CannotLoadSettingsError


def get_conf_path():
    return Path(user_config_dir(__name__)) / "wonfile.py"


class Settings(dict):
    # lower case settings are internal-only
    # upper case settings are user-configurable
    def __init__(self):
        super().__init__()
        self._settings_file = get_conf_path()
        self._user_tz = str(get_localzone())  # for user display
        self._internal_tz = "UTC"  # for internal storage and manipulation
        self._internal_dt_format = "%Y-%m-%d %H:%M:%S%z"

    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, key, value):
        self[key] = value

    def _create_settings_file(self):
        """
        Create settings file if absent
        """
        # make the parent first
        self._settings_file.parent.mkdir(parents=True, exist_ok=True)
        # write sample settings
        with self._settings_file.open(mode="w") as settings_file:
            settings_file.write(SETTINGS_HEADER)
            for setting in dir(default_settings):
                if setting.isupper():
                    settings_file.write(f'# {setting} = "{getattr(default_settings, setting)}"\n')

    def configure(self, user_settings=None):
        """
        Configuration
        """
        user_settings_module = None
        # create module
        if not self._settings_file.is_file():
            try:
                self._create_settings_file()
            except Exception as e:
                raise CannotCreateSettingsError(extra_detail=str(e))
        else:
            # load user settings module
            try:
                spec = spec_from_file_location(
                    self._settings_file.name, self._settings_file.resolve()
                )
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
