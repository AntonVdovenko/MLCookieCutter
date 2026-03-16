# MLCookieCutter Improvements Design

**Date:** 2026-03-16
**Branch:** claude/heuristic-dhawan
**Status:** Approved

---

## Overview

A critical audit of the MLCookieCutter template identified several bugs, inconsistencies, and missing features. This spec covers all confirmed changes grouped by area.

---

## 1. `cookiecutter.json` — New Variables & Default Fixes

### New variables

| Variable | Type | Default | Purpose |
|---|---|---|---|
| `author_name` | string | `"Your Name"` | Populates `pyproject.toml` authors field |
| `author_email` | string | `"your@email.com"` | Populates `pyproject.toml` authors field |
| `license` | choice | `"MIT"` | Options: MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, Proprietary |
| `keywords` | string | `""` | Comma-separated PyPI keywords, e.g. `machine-learning, mlops` |

### Default fixes

- `python_version`: `>=3.12` → `>=3.10` — aligns with `python_test_versions` default floor of `3.10`
- `python_test_versions`: unchanged (`3.10, 3.11, 3.12`)

**Rationale:** The previous defaults were inconsistent — requiring Python >=3.12 while attempting to test on 3.10 and 3.11.

---

## 2. Cookiecutter Hook — `hooks/pre_gen_project.py`

A pre-generation validation hook that prevents generating a project with an impossible CI matrix.

### Logic

1. Parse minimum Python version from `python_version` (strip operators: `>=`, `^`, `~=`, `==`)
2. Parse each version from `python_test_versions` (split on `,`, strip whitespace)
3. Compare: if any test version is below the minimum → `sys.exit(1)` with a descriptive error

### Error message format

```
ERROR: python_test_versions contains '3.10' but python_version requires >=3.11.
All test versions must be >= the minimum python_version.
Fix: either lower python_version (e.g. >=3.10) or remove versions below the minimum from python_test_versions.
```

### Edge cases

- Handles `>=3.10`, `^3.10`, `~=3.10`, `==3.10` formats
- Handles single-version test matrix (e.g. `3.12` only)
- Skips validation if `python_version` has no lower bound (e.g. hypothetical `<4.0`)

---

## 3. Dockerfile Fixes

File: `{{cookiecutter.directory_name}}/Dockerfile.base`

### Changes

1. **Remove dead code** — the first `FROM` block (orphaned multi-stage attempt, never referenced) is deleted entirely
2. **Parameterize Python version** — replace hardcoded `3.12` with a Jinja2 expression derived from `target_python_version`:
   - `py312` → `{{ cookiecutter.target_python_version[2:3] }}.{{ cookiecutter.target_python_version[3:] }}` → `3.12`
   - Works for any `pyXYZ` format
3. **Fix typo** — `Intall` → `Install` in comment

### Result (header of file)

```dockerfile
# Install uv
FROM python:{{ cookiecutter.target_python_version[2:3] }}.{{ cookiecutter.target_python_version[3:] }}-slim-bookworm AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
```

---

## 4. `pyproject.toml` Metadata

File: `{{cookiecutter.directory_name}}/pyproject.toml`

### New `[project]` fields

```toml
authors = [
    {name = "{{cookiecutter.author_name}}", email = "{{cookiecutter.author_email}}"}
]
license = {text = "{{cookiecutter.license}}"}
keywords = [
    {%- for kw in cookiecutter.keywords.split(',') if kw.strip() %}
    "{{ kw.strip() }}",
    {%- endfor %}
]
classifiers = [
    "Programming Language :: Python :: 3",
    {%- for v in cookiecutter.python_test_versions.split(',') %}
    "Programming Language :: Python :: {{ v.strip() }}",
    {%- endfor %}
    "License :: OSI Approved :: {{ cookiecutter.license }} License",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]
```

### License classifier mapping

| cookiecutter value | Classifier text |
|---|---|
| MIT | MIT License |
| Apache-2.0 | Apache Software License |
| GPL-3.0 | GNU General Public License v3 |
| BSD-3-Clause | BSD License |
| Proprietary | Other/Proprietary License |

This mapping is implemented directly in the template via a Jinja2 `if/elif` block for the classifiers line.

---

## 5. Pre-commit & CHANGELOG

### `.pre-commit-config.yaml`

Replace all `uvx ruff` invocations with `uv run ruff`. Rationale: ruff is declared in dev dependencies; `uv run` uses the pinned version from `uv.lock`, ensuring consistency between local dev and CI. `uvx` runs ruff independently and may use a different version.

### `CHANGELOG.md`

Add an empty `CHANGELOG.md` to the template. Tracked from project creation so semantic-release can append to it from the first release onward. Content:

```markdown
# Changelog
```

---

## 6. Generated README

File: `{{cookiecutter.directory_name}}/README.md`

### Sections

1. **Header**
   - `# {{cookiecutter.project_name}}`
   - `{{cookiecutter.project_description}}`
   - CI status badge (links to `ci.yml` workflow)
   - Python version badge (from `python_version`)

2. **Tooling Overview** — one paragraph per tool:
   - **uv** — fast Python package manager and virtual environment tool; manages dependencies and the `uv.lock` lockfile
   - **ruff** — linter and formatter; enforces code style and catches errors via pre-commit and CI
   - **hatch-vcs** — derives the package version from git tags; no manual version bumping needed
   - **pytest** — test runner; tests live in `tests/`
   - **pre-commit** — git hook framework; runs ruff and commit-msg validation on every commit
   - **python-semantic-release** — reads conventional commits to determine version bumps, writes `CHANGELOG.md`, tags releases, and publishes to GitHub Releases
   - **DVC** *(conditional — only rendered when `include_dvc == "true"`)* — data version control; tracks large files and datasets outside git, supports S3 remote storage; `dvclive` provides experiment tracking

3. **GitHub Actions**
   - **`ci.yml`** — triggered on pull requests; runs ruff lint check and pytest across the configured Python version matrix (`{{cookiecutter.python_test_versions}}`)
   - **`release.yml`** — triggered on push to `{{cookiecutter.default_branch}}`; runs python-semantic-release to bump version, update changelog, tag, and publish GitHub Release

4. **Getting Started**
   ```bash
   make init_project   # git init, uv sync, install pre-commit hooks
   uv run pytest       # run tests
   uv run ruff check . # lint
   uv run ruff format .# format
   ```

5. **Python Version Compatibility Warning**
   > **Note:** All versions listed in `python_test_versions` must be >= the minimum version in `python_version`. Mismatches will cause CI failures. This is validated at project generation time.

6. **License**
   - `This project is licensed under the {{cookiecutter.license}} license.`

---

## Summary of All Changes

| Area | Change | Severity fixed |
|---|---|---|
| `cookiecutter.json` | Fix `python_version` default from `>=3.12` to `>=3.10` | Critical |
| `cookiecutter.json` | Add `author_name`, `author_email`, `license`, `keywords` variables | High |
| `hooks/pre_gen_project.py` | New file: validates test versions >= python_version minimum | Critical |
| `Dockerfile.base` | Remove dead first FROM block | High |
| `Dockerfile.base` | Parameterize Python version from `target_python_version` | High |
| `Dockerfile.base` | Fix typo "Intall" | Low |
| `pyproject.toml` | Add authors, license, keywords, classifiers | High |
| `.pre-commit-config.yaml` | Replace `uvx ruff` with `uv run ruff` | Medium |
| `CHANGELOG.md` | Add empty boilerplate file | Medium |
| `README.md` | Full template with tooling docs, GitHub Actions docs, badges, warning | High |

---

## Out of Scope

- Semantic-release / hatch-vcs version configuration — confirmed working as-is by project owner
- Adding mypy or additional pre-commit hooks — not requested
- Root-level `.gitignore` for the cookiecutter template itself — minor, deferred
