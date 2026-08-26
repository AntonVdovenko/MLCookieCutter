# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}
{% if cookiecutter.include_ci == "true" %}
![CI](https://github.com/USERNAME/{{ cookiecutter.project_name }}/actions/workflows/ci.yml/badge.svg)
{%- endif %}
![Python](https://img.shields.io/badge/python->%3D{{ cookiecutter.python_version }}-blue)

## Documentation and Agentic Development

This repository is set up so humans and coding agents can preserve
implementation context across features, experiments, deployments, and debugging
sessions.

Start here:

1. Read this README for the repository overview.
2. Read `docs/SETUP_and_TESTING_GUIDE.md` for local setup and validation.
3. Read `docs/engineering-logs.md` before debugging or changing behavior.
4. Read the relevant human-written spec in `docs/feature-specs/` before
   implementing a feature, fix, or experiment change.

Agent instructions:

- Claude Code: `CLAUDE.md`
- Codex and terminal agents: `AGENTS.md`

Documentation map:

| Document | Purpose |
|---|---|
| `docs/engineering-logs.md` | Timestamped implementation context, setup oddities, deployment notes, experiment changes, and validation results. |
| `docs/feature-specs/` | Human-written feature, fix, task, and experiment specs. Agent additions use italics; reversals of human context use strikethrough. |
| `docs/C4_ARCHITECTURE.md` | Production architecture diagrams and service/data-flow context. Mandatory for production services. |
| `docs/API_DOCUMENTATION.md` | External integration contract. Mandatory for production services. |
| `docs/SETUP_and_TESTING_GUIDE.md` | Local setup, Docker, Kubernetes/Helm, smoke tests, regression tests, stress tests, and evaluation commands. |
| `docs/Dataset.md` | Dataset names, versions, paths, generation steps, and curation rationale for experiment repos. |
| `docs/Experiments.md` | Experiment plans, methods, phases, output paths, drawbacks, and open questions. |
| `docs/STATUS.md` | Live status of experiments and evaluation work. |
| `docs/Evaluation_and_findings.md` | Evaluation settings, benchmarks, results, and qualitative/quantitative findings. |

PR descriptions should point reviewers to the relevant docs. Review priority is
human-authored specs and context first, then agent-authored or agent-updated
architecture, API, setup, and engineering-log entries.

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
{% if cookiecutter.include_ci == "true" %}
### `ci.yml`
Triggered on pull requests to `{{ cookiecutter.default_branch }}`. Runs ruff lint and format checks, then runs pytest across the Python version matrix ({{ cookiecutter.python_test_versions }}).
{% endif %}
### `release.yml`
Triggered on push to `{{ cookiecutter.default_branch }}`. Runs python-semantic-release to determine the next version from commit messages, updates `CHANGELOG.md`, creates a git tag, builds the package, and publishes a GitHub Release.

## Project Structure

```
{{ cookiecutter.directory_name }}/
├── src/
│   └── {{ cookiecutter.package_name }}/ # Importable Python package
├── tests/            # Test files (pytest)
├── config/           # Configuration files (YAML, JSON, etc.)
├── data/             # Datasets (not tracked by git{% if cookiecutter.include_dvc == "true" %}; use DVC{% endif %})
├── models/           # Trained model artifacts
├── notebooks/        # Jupyter notebooks for exploration and analysis
├── docs/             # Project docs, specs, logs, and experiment records
├── CLAUDE.md         # Claude Code instructions
├── AGENTS.md         # Codex and terminal-agent instructions
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

> **Note:** All versions listed in `python_test_versions` ({{ cookiecutter.python_test_versions }}) must be >= the minimum `python_version` ({{ cookiecutter.python_version }}). Mismatches are rejected at project generation time. Keep the matrix on stable Python versions supported by GitHub Actions / `uv python install`.

## License

This project is licensed under the {{ cookiecutter.license }} license. See [LICENSE](LICENSE) for details.
