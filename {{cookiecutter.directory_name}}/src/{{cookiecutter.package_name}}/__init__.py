"""Source code of your project."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("{{ cookiecutter.project_name }}")
except PackageNotFoundError:
    # Deliberately NOT a plausible release number: dist metadata (hatch-vcs
    # from the git tag) is the only version channel; this sentinel means
    # "imported from a source tree without installed metadata".
    __version__ = "0.0.0+unknown"
