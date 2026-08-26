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
- **Agentic development docs** — generated docs, engineering logs, feature
  specs, `CLAUDE.md`, and `AGENTS.md` so Claude Code, Codex, and terminal
  agents follow the same implementation-context workflow

## Quick Start

```bash
pip install cookiecutter
cookiecutter gh:AntonVdovenko/MLCookieCutter
```

You will be prompted for:

| Variable | Description | Default |
|---|---|---|
| `directory_name` | Project directory name | `DS_project` |
| `project_name` | Distribution/project name for `pyproject.toml` | `default_project` |
| `package_name` | Python import package name under `src/` | derived from `project_name` |
| `project_description` | Short description | `default_description` |
| `author_name` | Author name (for LICENSE and pyproject.toml) | `Your Name` |
| `author_email` | Author email | `your@email.com` |
| `python_version` | Minimum Python version | `3.10` |
| `default_branch` | Git default branch | `main` |
| `license` | License type | `MIT` (also: Apache-2.0, GPL-3.0, BSD-3-Clause, Proprietary) |
| `keywords` | Comma-separated PyPI keywords | *(empty)* |
| `include_dvc` | Include DVC dependencies | `false` |
| `include_ci` | Include the PR CI workflow (`ci.yml`: ruff lint + pytest matrix); `release.yml` semantic versioning is always included | `true` |
| `python_test_versions` | Comma-separated Python versions for CI test matrix; spaces are optional | `3.10, 3.11, 3.12, 3.13, 3.14` |

Then initialize your project:

```bash
cd your_project
make init_project
```

This runs `git init`, `uv sync`, and installs pre-commit hooks.

## Generated Project Structure

```
your_project/
├── src/
│   └── package_name/ # Importable Python package
├── tests/            # Tests (pytest)
├── config/           # Configuration files
├── data/             # Datasets (gitignored)
├── models/           # Model artifacts
├── notebooks/        # Jupyter notebooks
├── docs/             # Docs, engineering logs, specs, API/setup/architecture, experiment records
├── CLAUDE.md         # Claude Code instructions
├── AGENTS.md         # Codex and terminal-agent instructions
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
- Keep the default CI matrix on stable Python minors that are available in GitHub Actions / `uv python install`. Add future versions such as `3.15` once the runner/tooling ecosystem supports them, rather than deriving versions automatically from the minimum Python version.

## Agentic Development Flow

Generated projects include a documentation workflow for human and agentic
development:

- `docs/engineering-logs.md` records timestamped implementation context and is
  the first file agents should read during debugging.
- `docs/feature-specs/` stores human-written specs for feature, fix, task, and
  experiment work. Agent additions use italics, and reversals of human context
  use strikethrough.
- `docs/C4_ARCHITECTURE.md`, `docs/API_DOCUMENTATION.md`, and
  `docs/SETUP_and_TESTING_GUIDE.md` cover production architecture, external
  contracts, setup, deployment, and validation.
- `docs/Dataset.md`, `docs/Experiments.md`, `docs/STATUS.md`, and
  `docs/Evaluation_and_findings.md` cover experiment and evaluation repos.
- `CLAUDE.md` and `AGENTS.md` make the same rules visible to Claude Code, Codex,
  and other terminal agents.

PR descriptions should point reviewers to the relevant docs, with priority on
human-authored specs and context.
