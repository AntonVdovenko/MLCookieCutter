"""Source code of your project."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("{{ cookiecutter.project_name }}")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"  # updated by semantic-release
