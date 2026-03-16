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

### Variable changes

- **`python_version`**: changed from constraint format (`>=3.12`) to bare version number (`3.12`). Default: `3.10`. All derived usages:
  - `requires-python` in `pyproject.toml` → `">={{ cookiecutter.python_version }}"`
  - ruff `target-version` → `"py{{ cookiecutter.python_version | replace('.', '') }}"` (e.g. `py310`)
  - Docker image tag → `python:{{ cookiecutter.python_version }}-slim-bookworm`
- **`target_python_version`**: **removed entirely** — derived from `python_version` via Jinja2 filters
- `python_test_versions`: unchanged (`3.10, 3.11, 3.12`)

**Rationale:** The previous defaults were inconsistent — requiring Python >=3.12 while testing on 3.10 and 3.11. Having both `python_version` and `target_python_version` as separate inputs was redundant and error-prone; a single `python_version` variable with derivations eliminates duplication.

---

## 2. Cookiecutter Hook — `hooks/pre_gen_project.py`

A pre-generation validation hook that prevents generating a project with an impossible CI matrix.

**File placement:** `hooks/pre_gen_project.py` at the cookiecutter **root** (same level as `cookiecutter.json`), not inside the template directory. The `hooks/` directory must be created if it does not exist.

### Logic

Since `python_version` is now a bare version number (e.g. `3.10`), the hook is straightforward:

1. Parse `python_version` as `packaging.version.Version` — no operator stripping needed
2. Parse each version from `python_test_versions` (split on `,`, strip whitespace) as `packaging.version.Version`
3. If any test version is below `python_version` → `sys.exit(1)` with a descriptive error

### Error message format

```
ERROR: python_test_versions contains '3.10' but python_version is 3.11.
All test versions must be >= python_version.
Fix: either lower python_version (e.g. 3.10) or remove versions below the minimum from python_test_versions.
```

### Edge cases

| Input | Behaviour |
|---|---|
| `python_version = 3.10`, test versions `3.10, 3.11, 3.12` | All valid |
| `python_version = 3.11`, test versions `3.10, 3.11, 3.12` | Error: `3.10` is below `3.11` |
| Single version in matrix (e.g. `3.12`) | Handled correctly |
| Invalid version string (e.g. `abc`) | Error with descriptive message |

---

## 3. Dockerfile Fixes

File: `{{cookiecutter.directory_name}}/Dockerfile.base`

### Changes

1. **Remove dead code** — the first `FROM` block (orphaned multi-stage attempt, never referenced) is deleted entirely
2. **Parameterize Python version** — replace hardcoded `3.12` with `{{ cookiecutter.python_version }}` (now a bare version number like `3.10`)
3. **Fix typo** — `Intall` → `Install` in comment

### Result (full file — body unchanged from current, only header modified)

```dockerfile
# Install uv
FROM python:{{ cookiecutter.python_version }}-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
```

The `AS base` stage name is removed — there is only one stage, so a name adds no value. The rest of the file body (apt-get, uv sync, etc.) is preserved unchanged.

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
    {%- if cookiecutter.license == "MIT" %}
    "License :: OSI Approved :: MIT License",
    {%- elif cookiecutter.license == "Apache-2.0" %}
    "License :: OSI Approved :: Apache Software License",
    {%- elif cookiecutter.license == "GPL-3.0" %}
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    {%- elif cookiecutter.license == "BSD-3-Clause" %}
    "License :: OSI Approved :: BSD License",
    {%- elif cookiecutter.license == "Proprietary" %}
    "License :: Other/Proprietary License",
    {%- endif %}
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]
```

### License classifier mapping

| cookiecutter value | PyPI classifier string |
|---|---|
| MIT | `License :: OSI Approved :: MIT License` |
| Apache-2.0 | `License :: OSI Approved :: Apache Software License` |
| GPL-3.0 | `License :: OSI Approved :: GNU General Public License v3 (GPLv3)` |
| BSD-3-Clause | `License :: OSI Approved :: BSD License` |
| Proprietary | `License :: Other/Proprietary License` (no OSI Approved prefix) |

Note: `GPL-3.0` is stored as the SPDX identifier in `license = {text = ...}`. The deprecated short-form `GPL-3.0` is used for user-friendliness in the cookiecutter choice; the classifier uses the full correct PyPI string.

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
   uv run ruff format . # format
   ```

5. **Python Version Compatibility Warning**
   > **Note:** All versions listed in `python_test_versions` must be >= the minimum version in `python_version`. Mismatches will cause CI failures. This is validated at project generation time.

6. **License**
   - `This project is licensed under the {{cookiecutter.license}} license.`

---

## Summary of All Changes

| Area | Change | Severity fixed |
|---|---|---|
| `cookiecutter.json` | Change `python_version` to bare version (`3.10`), remove `target_python_version` | Critical |
| `cookiecutter.json` | Add `author_name`, `author_email`, `license`, `keywords` variables | High |
| `hooks/pre_gen_project.py` | New file: validates test versions >= python_version minimum | Critical |
| `Dockerfile.base` | Remove dead first FROM block | High |
| `Dockerfile.base` | Parameterize Python version from `python_version` | High |
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
