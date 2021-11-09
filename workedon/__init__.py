"""Top-level package for workedon."""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__author__ = "Visesh Prasad"
__email__ = "viseshrprasad@gmail.com"
__name__ = "workedon"
__version__ = importlib_metadata.version(__name__)
