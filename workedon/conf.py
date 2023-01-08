from importlib.machinery import SourceFileLoader
from pathlib import Path

from platformdirs import user_config_dir
from tzlocal import get_localzone

from . import __name__
from . import default_settings
from .constants import SETTINGS_HEADER
from .exceptions import CannotCreateSettingsError, CannotLoadSettingsError


class Settings(dict):
    # lower case settings are internal-only
    # upper case settings are user-configurable
    def __init__(self):
        super().__init__()
        self.settings_file = Path(user_config_dir(__name__)) / "wonfile.py"
        self.user_tz = str(get_localzone())  # for user display
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
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        # write sample settings
        with self.settings_file.open(mode="w") as settings_file:
            settings_file.write(SETTINGS_HEADER)
            for setting in dir(default_settings):
                if setting.isupper():
                    settings_file.write(
                        f'# {setting} = "{getattr(default_settings, setting)}"\n'
                    )

    def configure(self, user_settings=None):
        """
        Configuration
        """
        user_settings_module = None
        # create module
        if not self.settings_file.is_file():
            try:
                self._create_settings_file()
            except Exception as e:
                raise CannotCreateSettingsError(extra_detail=str(e))
        else:
            # load user settings module
            try:
                user_settings_module = SourceFileLoader(
                    self.settings_file.name,
                    str(self.settings_file.resolve()),  # abs path
                ).load_module()
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
