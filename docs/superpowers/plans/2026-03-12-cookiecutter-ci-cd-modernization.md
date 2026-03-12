# MLCookieCutter CI/CD & Tooling Modernization Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port CI/CD, pre-commit, semantic versioning, and comprehensive linting from xhai-llm-utils into the MLCookieCutter template with configurable DVC, test matrix, and branch name variables.

**Architecture:** Direct port of proven xhai-llm-utils configurations into Cookiecutter Jinja2 templates. The template generates projects with hatchling+hatch-vcs build system, python-semantic-release for automated versioning, GitHub Actions for CI/CD, and comprehensive pre-commit hooks including conventional commit enforcement. Jinja2 conditionals handle optional DVC dependencies and configurable test matrix.

**Tech Stack:** Cookiecutter (Jinja2 templates), hatchling, hatch-vcs, python-semantic-release, GitHub Actions, pre-commit, Ruff, uv

**Spec:** `docs/superpowers/specs/2026-03-12-cookiecutter-ci-cd-modernization-design.md`

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `cookiecutter.json` | Modify | Template variables (add `default_branch`, `include_dvc`, `python_test_versions`) |
| `{{cookiecutter.directory_name}}/pyproject.toml` | Rewrite | Build system, deps, tool configs (ruff, pytest, semantic-release, hatch-vcs) |
| `{{cookiecutter.directory_name}}/.pre-commit-config.yaml` | Rewrite | All pre-commit hooks (ruff, uv-lock, file safety, conventional commits) |
| `{{cookiecutter.directory_name}}/Makefile` | Modify | Add commit-msg hook type to pre-commit install |
| `{{cookiecutter.directory_name}}/src/__init__.py` | Rewrite | Package version via importlib.metadata with semantic-release fallback |
| `{{cookiecutter.directory_name}}/.github/workflows/ci.yml` | Create | CI pipeline: lint, test matrix, build |
| `{{cookiecutter.directory_name}}/.github/workflows/release.yml` | Create | Semantic release pipeline: version bump, tag, GitHub release |

**Important context for implementers:**
- All file paths containing `{{cookiecutter.directory_name}}` are Jinja2 templates — the `{{` and `}}` are literal Cookiecutter syntax, not placeholders you fill in.
- Similarly, `{{cookiecutter.project_name}}`, `{{cookiecutter.default_branch}}`, etc. inside file contents are literal Jinja2 expressions that Cookiecutter resolves at project generation time.
- The reference implementation is at `/home/h100mleva/xhai-llm-utils/` — consult it if any detail is unclear.
- Before starting, create a new branch: `git checkout -b feat/ci-cd-modernization`
- Use conventional commit messages for all commits (e.g., `feat:`, `build:`, `ci:`).

---

## Chunk 1: Foundation — Branch, Variables, Build System, and Version

### Task 1: Create feature branch and update cookiecutter.json

**Files:**
- Modify: `cookiecutter.json`

- [ ] **Step 1: Create feature branch**

```bash
git checkout -b feat/ci-cd-modernization
```

- [ ] **Step 2: Update cookiecutter.json with new variables**

Replace the contents of `cookiecutter.json` with:

```json
{
    "directory_name": "DS_project",
    "project_name": "default_project",
    "project_description": "default_description",
    "python_version": ">=3.12",
    "target_python_version": "py312",
    "default_branch": "main",
    "include_dvc": false,
    "python_test_versions": "3.10, 3.11, 3.12"
}
```

- [ ] **Step 3: Commit**

```bash
git add cookiecutter.json
git commit -m "feat: add cookiecutter variables for branch, DVC, and test matrix"
```

---

### Task 2: Rewrite pyproject.toml with build system, deps, and tool configs

**Files:**
- Rewrite: `{{cookiecutter.directory_name}}/pyproject.toml`

- [ ] **Step 1: Rewrite pyproject.toml**

Replace the entire contents of `{{cookiecutter.directory_name}}/pyproject.toml` with:

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "{{cookiecutter.project_name}}"
dynamic = ["version"]
description = "{{cookiecutter.project_description}}"
readme = "README.md"
requires-python = "{{cookiecutter.python_version}}"
dependencies = []

# ---------- UV Configuration ----------
[dependency-groups]
dev = [
    "pytest>=8.3.3",
    "ruff>=0.9",
    "pre-commit>=4.0.1",
    "build",
    "twine",
    "loguru>=0.7.2",
    "pyyaml>=6.0.2",
{%- if cookiecutter.include_dvc == "true" %}
    "dvc[s3]>=3.55.2",
    "dvclive>=3.48.0",
    "gto>=1.7.1",
{%- endif %}
]

[tool.uv]
default-groups = ["dev"]

# ---------- Hatch Version Configuration ----------
[tool.hatch.version]
source = "vcs"

[tool.hatch.version.raw-options]
version_scheme = "guess-next-dev"
local_scheme = "no-local-version"

# ---------- Ruff Configuration ----------
[tool.ruff]
target-version = "{{cookiecutter.target_python_version}}"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "PTH",    # flake8-use-pathlib
    "ERA",    # eradicate (commented out code)
    "PL",     # Pylint
    "RUF",    # Ruff-specific rules
]
ignore = [
    "E501",    # line too long (handled by formatter)
    "PLR0913", # too many arguments
    "PLR2004", # magic value comparison
    "PLR0912", # too many branches
    "PLR0915", # too many statements
    "PLR0911", # too many return statements
    "PLC0415", # import not at top-level (lazy imports are intentional)
    "RUF001",  # ambiguous unicode chars (common in prompt strings)
    "RUF002",  # ambiguous unicode chars in docstrings
    "RUF003",  # ambiguous unicode chars in comments
    "RUF005",  # consider unpacking instead of concatenation
    "RUF006",  # dangling asyncio task
    "RUF013",  # implicit Optional
    "RUF059",  # unused unpacked variables
    "PTH103",  # os.makedirs → Path.mkdir
    "PTH110",  # os.path.exists → Path.exists
    "PTH118",  # os.path.join → Path /
    "PTH120",  # os.path.dirname → Path.parent
    "PTH123",  # open() vs Path.open()
    "PTH207",  # glob → Path.glob
    "PLE1205", # too many args for logging format string
    "ERA001",  # commented-out code (too noisy)
    "B905",    # zip() without strict=
    "B006",    # mutable default argument (list/dict literal)
    "B007",    # unused loop variable
    "SIM105",  # use contextlib.suppress
    "SIM115",  # use context manager for open
    "SIM117",  # use single with statement
    "SIM118",  # use key in dict instead of dict.keys()
    "SIM108",  # use ternary operator
    "PLW2901", # overwriting loop variable
    "PLW3301", # nested min/max
    "PLW0603", # global statement
    "E741",    # ambiguous variable name
    "TC002",   # move third-party import into TYPE_CHECKING (risky at runtime)
    "TC003",   # move stdlib import into TYPE_CHECKING (risky at runtime)
    "RUF057",  # unnecessary round on int
    "B039",    # mutable ContextVar default
    "B034",    # re.sub with count without flags
]

[tool.ruff.lint.isort]
known-first-party = ["src"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["ARG", "PLR2004"]
"**/conftest.py" = ["ARG"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
docstring-code-format = true

# ---------- Pytest Configuration ----------
[tool.pytest.ini_options]
testpaths = ["tests"]

# ---------- Semantic Release Configuration ----------
[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
version_variables = ["src/__init__.py:__version__"]
branch = "{{cookiecutter.default_branch}}"
tag_format = "v{version}"
commit_message = "chore(release): {version}\n\nAutomatically generated by python-semantic-release"
build_command = """
    uv lock --upgrade-package {{cookiecutter.project_name}}
    git add uv.lock
    uv build
"""

[tool.semantic_release.changelog.default_templates]
changelog_file = "CHANGELOG.md"

[tool.semantic_release.remote]
type = "github"
token = { env = "GH_TOKEN" }

[tool.semantic_release.publish]
upload_to_vcs_release = true
```

- [ ] **Step 2: Commit**

```bash
git add "{{cookiecutter.directory_name}}/pyproject.toml"
git commit -m "build: rewrite pyproject.toml with hatchling, hatch-vcs, ruff, and semantic-release"
```

---

### Task 3: Update src/__init__.py with version management

**Files:**
- Rewrite: `{{cookiecutter.directory_name}}/src/__init__.py`

- [ ] **Step 1: Rewrite src/__init__.py**

Replace the contents of `{{cookiecutter.directory_name}}/src/__init__.py` with:

```python
"""Source code of your project."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("{{ cookiecutter.project_name }}")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"  # updated by semantic-release
```

- [ ] **Step 2: Commit**

```bash
git add "{{cookiecutter.directory_name}}/src/__init__.py"
git commit -m "feat: add version management via importlib.metadata"
```

---

## Chunk 2: Pre-commit Hooks and Makefile

### Task 4: Rewrite .pre-commit-config.yaml

**Files:**
- Rewrite: `{{cookiecutter.directory_name}}/.pre-commit-config.yaml`

- [ ] **Step 1: Rewrite .pre-commit-config.yaml**

Replace the entire contents of `{{cookiecutter.directory_name}}/.pre-commit-config.yaml` with:

```yaml
# See https://pre-commit.com for more information
repos:
  # Ruff linter and formatter (local, using uvx)
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff check
        entry: uvx ruff check --fix --exit-non-zero-on-fix
        language: system
        types: [python]
        exclude: '\.ipynb$'
      - id: ruff-format
        name: ruff format
        entry: uvx ruff format
        language: system
        types: [python]
        exclude: '\.ipynb$'

  # UV lock file maintenance
  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.9.26
    hooks:
      - id: uv-lock
        name: Check uv.lock is up to date

  # General file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: debug-statements
      - id: detect-private-key

  # Conventional commit message validation
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.0.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert]

ci:
  autofix_commit_msg: "style: auto-fix by pre-commit hooks"
  autoupdate_commit_msg: "chore: update pre-commit hooks"
```

- [ ] **Step 2: Commit**

```bash
git add "{{cookiecutter.directory_name}}/.pre-commit-config.yaml"
git commit -m "build: replace pre-commit config with comprehensive hook suite"
```

---

### Task 5: Update Makefile with commit-msg hook install

**Files:**
- Modify: `{{cookiecutter.directory_name}}/Makefile`

- [ ] **Step 1: Update init_project target**

**Important:** Makefiles require tab indentation, not spaces. Ensure the recipe lines under `init_project:` use actual tab characters.

In `{{cookiecutter.directory_name}}/Makefile`, replace the `init_project` target:

Old:
```makefile
init_project:
	git init
	uv sync
	uv run pre-commit install
```

New:
```makefile
init_project:
	git init
	uv sync
	uv run pre-commit install
	uv run pre-commit install --hook-type commit-msg
```

- [ ] **Step 2: Commit**

```bash
git add "{{cookiecutter.directory_name}}/Makefile"
git commit -m "build: add commit-msg hook type to pre-commit install"
```

---

## Chunk 3: GitHub Actions Workflows

### Task 6: Create CI workflow

**Files:**
- Create: `{{cookiecutter.directory_name}}/.github/workflows/ci.yml`

- [ ] **Step 1: Create .github/workflows directory**

```bash
mkdir -p "{{cookiecutter.directory_name}}/.github/workflows"
```

- [ ] **Step 2: Create ci.yml**

Create `{{cookiecutter.directory_name}}/.github/workflows/ci.yml` with:

```yaml
name: CI

on:
  pull_request:
    branches: [{{ cookiecutter.default_branch }}]

concurrency:
  group: {% raw %}${{ github.workflow }}-${{ github.ref }}{% endraw %}
  cancel-in-progress: true

env:
  UV_CACHE_DIR: /tmp/.uv-cache

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --frozen --group dev

      - name: Run ruff check
        run: uv run ruff check --output-format=github .

      - name: Run ruff format check
        run: uv run ruff format --check .

  test:
    name: Test (Python {% raw %}${{ matrix.python-version }}{% endraw %})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: [{{ cookiecutter.python_test_versions.split(', ') | map('tojson') | join(', ') }}]

    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - name: Set up Python {% raw %}${{ matrix.python-version }}{% endraw %}
        run: uv python install {% raw %}${{ matrix.python-version }}{% endraw %}

      - name: Install dependencies
        run: uv sync --frozen --group dev

      - name: Run tests
        run: uv run pytest --tb=short -v

  build:
    name: Build Package
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up uv
        uses: astral-sh/setup-uv@v5

      - name: Build package
        run: uv build

      - name: Check package
        run: |
          uv tool install twine
          twine check dist/*

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

**Important note for implementer:** The `{% raw %}` and `{% endraw %}` tags are Jinja2 escape blocks — they tell Cookiecutter to output the `${{ ... }}` GitHub Actions expressions literally without trying to resolve them as Jinja2 variables.

The matrix line `[{{ cookiecutter.python_test_versions.split(', ') | map('tojson') | join(', ') }}]` converts the comma-separated string `"3.10, 3.11, 3.12"` into a YAML array `["3.10", "3.11", "3.12"]` at generation time. The outer `[` and `]` brackets are literal YAML — the Jinja2 expression produces the inner comma-separated quoted values.

- [ ] **Step 3: Commit**

```bash
git add "{{cookiecutter.directory_name}}/.github/workflows/ci.yml"
git commit -m "ci: add CI workflow with lint, test matrix, and build jobs"
```

---

### Task 7: Create release workflow

**Files:**
- Create: `{{cookiecutter.directory_name}}/.github/workflows/release.yml`

- [ ] **Step 1: Create release.yml**

Create `{{cookiecutter.directory_name}}/.github/workflows/release.yml` with:

```yaml
name: Semantic Release

on:
  push:
    branches: [{{ cookiecutter.default_branch }}]

permissions:
  contents: write
  id-token: write

env:
  UV_CACHE_DIR: /tmp/.uv-cache

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    concurrency: release

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}

      - name: Configure git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Set up uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: |
          uv sync --frozen --group dev
          uv pip install python-semantic-release

      - name: Python Semantic Release
        id: release
        env:
          GH_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}
        run: |
          VERSION=$(uv run semantic-release version --print)
          if [ -n "$VERSION" ]; then
            echo "released=true" >> $GITHUB_OUTPUT
            echo "version=$VERSION" >> $GITHUB_OUTPUT
            uv run semantic-release version --no-push
            uv lock --upgrade-package {{ cookiecutter.project_name }}
            git add uv.lock
            git commit --amend --no-edit
            git tag -f "v$VERSION"
            git push origin {{ cookiecutter.default_branch }} --tags
          else
            echo "released=false" >> $GITHUB_OUTPUT
          fi

      - name: Build package
        if: {% raw %}steps.release.outputs.released == 'true'{% endraw %}
        run: uv build

      - name: Upload to GitHub Release
        if: {% raw %}steps.release.outputs.released == 'true'{% endraw %}
        env:
          GH_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}
        run: |
          gh release create "v{% raw %}${{ steps.release.outputs.version }}{% endraw %}" dist/* \
            --title "v{% raw %}${{ steps.release.outputs.version }}{% endraw %}" \
            --generate-notes
```

- [ ] **Step 2: Commit**

```bash
git add "{{cookiecutter.directory_name}}/.github/workflows/release.yml"
git commit -m "ci: add semantic release workflow with automated GitHub releases"
```

---

## Chunk 4: Validation

### Task 8: Validate the template generates correctly

- [ ] **Step 1: Install cookiecutter if not available**

```bash
uv tool install cookiecutter
```

- [ ] **Step 2: Generate a test project with default settings**

```bash
cd /tmp
cookiecutter /home/h100mleva/MLCookieCutter --no-input
```

Expected: A `DS_project/` directory is created with all files.

- [ ] **Step 3: Verify generated pyproject.toml**

Read `/tmp/DS_project/pyproject.toml` and check ALL of the following:
- `[build-system]` has `hatchling` and `hatch-vcs`
- `dynamic = ["version"]` is present (no hardcoded `version = "0.1.0"`)
- `[dependency-groups]` section exists with `dev = [...]` (NOT old `[tool.uv] dev-dependencies`)
- `[tool.uv]` contains `default-groups = ["dev"]`
- `interrogate` does NOT appear anywhere in the file
- DVC deps (`dvc`, `dvclive`, `gto`) are NOT present (include_dvc defaults to false)
- Ruff config has full rule set (14 select groups, 38 ignore rules)
- `[tool.semantic_release]` is complete with all nested sections: `changelog.default_templates`, `remote`, `publish`
- `[tool.pytest.ini_options]` has `testpaths = ["tests"]`

```bash
cat /tmp/DS_project/pyproject.toml
```

- [ ] **Step 4: Verify generated pre-commit config**

Read `/tmp/DS_project/.pre-commit-config.yaml` and check:
- All 4 hook groups present: ruff (local), uv-lock, pre-commit-hooks, conventional-pre-commit
- Ruff hooks use `language: system` and `entry: uvx ruff ...`
- `ci:` block present with `autofix_commit_msg` and `autoupdate_commit_msg`

```bash
cat /tmp/DS_project/.pre-commit-config.yaml
```

- [ ] **Step 5: Verify generated CI workflow**

Read `/tmp/DS_project/.github/workflows/ci.yml` and check:
- Triggers on PRs to `main`
- `concurrency` block present with `cancel-in-progress: true`
- `UV_CACHE_DIR: /tmp/.uv-cache` env var set
- `astral-sh/setup-uv@v5` with `enable-cache: true` and `cache-dependency-glob: "uv.lock"`
- Test matrix has `["3.10", "3.11", "3.12"]`
- Build job has `fetch-depth: 0`
- GitHub Actions expressions (`${{ ... }}`) are rendered literally (not eaten by Jinja2)
- `{% raw %}` / `{% endraw %}` tags are NOT present in output

```bash
cat /tmp/DS_project/.github/workflows/ci.yml
```

- [ ] **Step 6: Verify generated release workflow**

Read `/tmp/DS_project/.github/workflows/release.yml` and check:
- Triggers on push to `main`
- `permissions: contents: write` and `id-token: write` present
- `concurrency: release` present
- Checkout has `fetch-depth: 0` and `token: ${{ secrets.GITHUB_TOKEN }}`
- Git configured as `github-actions[bot]`
- Semantic release flow: `version --print`, then `version --no-push`, `uv lock --upgrade-package default_project`, amend, force-tag, push
- `uv lock --upgrade-package default_project` uses the correct project name
- GitHub Actions expressions are rendered literally
- `{% raw %}` / `{% endraw %}` tags are NOT present in output

```bash
cat /tmp/DS_project/.github/workflows/release.yml
```

- [ ] **Step 7: Verify generated src/__init__.py**

Check that importlib.metadata version retrieval is present with `default_project` as the package name and `"0.0.0.dev0"` fallback.

```bash
cat /tmp/DS_project/src/__init__.py
```

- [ ] **Step 8: Verify generated Makefile**

Check that `init_project` includes both `pre-commit install` and `pre-commit install --hook-type commit-msg`.

```bash
cat /tmp/DS_project/Makefile
```

- [ ] **Step 9: Generate a test project WITH DVC**

```bash
cd /tmp
cookiecutter /home/h100mleva/MLCookieCutter --no-input include_dvc=true -o /tmp/DS_project_dvc
```

Verify DVC deps are present in pyproject.toml:

```bash
grep -E "dvc|dvclive|gto" /tmp/DS_project_dvc/DS_project/pyproject.toml
```

Expected: Lines containing `dvc[s3]>=3.55.2`, `dvclive>=3.48.0`, `gto>=1.7.1`.

- [ ] **Step 10: Generate a test project with custom branch name**

```bash
cd /tmp
cookiecutter /home/h100mleva/MLCookieCutter --no-input default_branch=develop -o /tmp/DS_project_branch
```

Verify the branch name is substituted in all 3 locations:

```bash
grep "develop" /tmp/DS_project_branch/DS_project/.github/workflows/ci.yml
grep "develop" /tmp/DS_project_branch/DS_project/.github/workflows/release.yml
grep "develop" /tmp/DS_project_branch/DS_project/pyproject.toml
```

Expected: Each grep finds at least one match with `develop`.

- [ ] **Step 11: Clean up test projects**

```bash
rm -rf /tmp/DS_project /tmp/DS_project_dvc /tmp/DS_project_branch
```

- [ ] **Step 12: Fix any issues found during validation**

If any validation step above failed, go back and fix the relevant template file, then re-run ALL validation steps (not just the failing one) to catch regressions.

- [ ] **Step 13: Final commit (if fixes were needed)**

Only if changes were made during validation:

```bash
git add -A
git commit -m "fix: resolve template generation issues found during validation"
```
