# MLCookieCutter

A [cookiecutter](https://cookiecutter.readthedocs.io/) template for bootstrapping Python ML/Data Science projects with modern tooling.

## What You Get

A ready-to-use project with:

- **[uv](https://docs.astral.sh/uv/)** — fast dependency management with lockfile
- **[ruff](https://docs.astral.sh/ruff/)** — linting and formatting
- **[hatch-vcs](https://github.com/ofek/hatch-vcs)** — automatic versioning from git tags
- **[pytest](https://docs.pytest.org/)** — testing
- **[pre-commit](https://pre-commit.com/)** — git hooks for code quality and conventional commits
- **[python-semantic-release](https://python-semantic-release.readthedocs.io/)** — automated changelog and GitHub releases
- **[DVC](https://dvc.org/)** *(optional)* — data version control with S3 support
- **GitHub Actions** — CI (lint + test matrix) and automated release workflows
- **Docker** — base Dockerfile with uv

## Quick Start

```bash
pip install cookiecutter
cookiecutter gh:AntonVdovenko/MLCookieCutter
```

You will be prompted for:

| Variable | Description | Default |
|---|---|---|
| `directory_name` | Project directory name | `DS_project` |
| `project_name` | Python package name | `default_project` |
| `project_description` | Short description | `default_description` |
| `author_name` | Author name (for LICENSE and pyproject.toml) | `Your Name` |
| `author_email` | Author email | `your@email.com` |
| `python_version` | Minimum Python version | `3.10` |
| `default_branch` | Git default branch | `main` |
| `license` | License type | `MIT` (also: Apache-2.0, GPL-3.0, BSD-3-Clause, Proprietary) |
| `keywords` | Comma-separated PyPI keywords | *(empty)* |
| `include_dvc` | Include DVC dependencies | `false` |
| `python_test_versions` | Python versions for CI test matrix | `3.10, 3.11, 3.12` |

Then initialize your project:

```bash
cd your_project
make init_project
```

This runs `git init`, `uv sync`, and installs pre-commit hooks.

## Generated Project Structure

```
your_project/
├── src/              # Source code
├── tests/            # Tests (pytest)
├── config/           # Configuration files
├── data/             # Datasets (gitignored)
├── models/           # Model artifacts
├── notebooks/        # Jupyter notebooks
├── docs/             # Documentation
├── .github/workflows # CI and release workflows
├── pyproject.toml    # Project metadata and tool config
├── Makefile          # Dev commands
├── Dockerfile.base   # Docker image
├── LICENSE           # Auto-generated from chosen license
├── CHANGELOG.md      # Auto-updated by semantic-release
└── README.md         # Project docs with tooling overview
```

## Validation

The template validates your inputs at generation time:
- All `python_test_versions` must be >= `python_version`. If you set `python_version` to `3.11` but include `3.10` in the test matrix, the template will error before generating.
