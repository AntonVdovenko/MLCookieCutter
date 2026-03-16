# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

![CI](https://github.com/USERNAME/{{ cookiecutter.project_name }}/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python->%3D{{ cookiecutter.python_version }}-blue)

## Tooling

This project uses the following tools:

### [uv](https://docs.astral.sh/uv/)
Fast Python package manager and virtual environment tool. Manages dependencies via `pyproject.toml` and locks them in `uv.lock` for reproducible installs.

### [ruff](https://docs.astral.sh/ruff/)
Linter and code formatter. Enforces code style and catches common errors. Runs automatically via pre-commit hooks and in CI.

### [hatch-vcs](https://github.com/ofek/hatch-vcs)
Derives the package version from git tags automatically. No manual version bumping needed — just tag a release and the version is resolved at build time.

### [pytest](https://docs.pytest.org/)
Test runner. Tests live in the `tests/` directory. Run with `uv run pytest`.

### [pre-commit](https://pre-commit.com/)
Git hook framework. Runs ruff linting/formatting, YAML/TOML validation, and conventional commit message checks on every commit.

### [python-semantic-release](https://python-semantic-release.readthedocs.io/)
Automated release tool. Reads [conventional commits](https://www.conventionalcommits.org/) to determine version bumps, generates `CHANGELOG.md`, creates git tags, and publishes GitHub Releases.

{%- if cookiecutter.include_dvc == "true" %}

### [DVC](https://dvc.org/)
Data Version Control. Tracks large files and datasets outside git with support for S3 remote storage. [DVCLive](https://dvc.org/doc/dvclive) provides experiment tracking and metric logging.
{%- endif %}

## GitHub Actions

### `ci.yml`
Triggered on pull requests to `{{ cookiecutter.default_branch }}`. Runs ruff lint and format checks, then runs pytest across the Python version matrix ({{ cookiecutter.python_test_versions }}).

### `release.yml`
Triggered on push to `{{ cookiecutter.default_branch }}`. Runs python-semantic-release to determine the next version from commit messages, updates `CHANGELOG.md`, creates a git tag, builds the package, and publishes a GitHub Release.

## Project Structure

```
{{ cookiecutter.directory_name }}/
├── src/              # Source code
├── tests/            # Test files (pytest)
├── config/           # Configuration files (YAML, JSON, etc.)
├── data/             # Datasets (not tracked by git{% if cookiecutter.include_dvc == "true" %}; use DVC{% endif %})
├── models/           # Trained model artifacts
├── notebooks/        # Jupyter notebooks for exploration and analysis
├── docs/             # Project documentation
├── pyproject.toml    # Project metadata and tool configuration
├── Makefile          # Common development commands
└── Dockerfile.base   # Docker image definition
```

## Getting Started

```bash
make init_project    # git init, uv sync, install pre-commit hooks
uv run pytest        # run tests
uv run ruff check .  # lint
uv run ruff format . # format
```

> **Note:** All versions listed in `python_test_versions` ({{ cookiecutter.python_test_versions }}) must be >= the minimum `python_version` ({{ cookiecutter.python_version }}). Mismatches will cause CI failures. This is validated at project generation time.

## License

This project is licensed under the {{ cookiecutter.license }} license. See [LICENSE](LICENSE) for details.
