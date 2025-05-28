"""The version module for the workedon package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("workedon")
except PackageNotFoundError:  # pragma: no cover
    # Fallback for local dev or editable installs
    __version__ = "0.0.0"
