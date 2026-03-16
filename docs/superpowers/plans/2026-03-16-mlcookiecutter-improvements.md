# MLCookieCutter Improvements Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix bugs, add missing metadata, and improve the MLCookieCutter template with validation hooks, LICENSE file, and comprehensive README.

**Architecture:** This is a cookiecutter template project. All changes are to template files (Jinja2) and cookiecutter configuration. A pre-gen hook validates inputs, a post-gen hook handles year substitution in LICENSE. Testing is done by running `cookiecutter` against the template and verifying generated output.

**Tech Stack:** Cookiecutter (Jinja2 templates), Python (hooks), TOML, YAML, Dockerfile

**Spec:** `docs/superpowers/specs/2026-03-16-mlcookiecutter-improvements-design.md`

---

## File Map

| Action | File | Responsibility |
|---|---|---|
| Modify | `cookiecutter.json` | Add new variables, change `python_version` format, remove `target_python_version` |
| Create | `hooks/pre_gen_project.py` | Validate test versions >= python_version |
| Create | `hooks/post_gen_project.py` | Replace `{YEAR}` placeholder in LICENSE |
| Modify | `{{cookiecutter.directory_name}}/Dockerfile.base` | Remove dead code, parameterize version, fix typo |
| Modify | `{{cookiecutter.directory_name}}/pyproject.toml` | Update derivations, add metadata fields |
| Modify | `{{cookiecutter.directory_name}}/.pre-commit-config.yaml` | Replace `uvx` with `uv run`, update comment |
| Modify | `{{cookiecutter.directory_name}}/.github/workflows/ci.yml` | Parameterize hardcoded Python 3.12 |
| Modify | `{{cookiecutter.directory_name}}/.github/workflows/release.yml` | Parameterize hardcoded Python 3.12 |
| Create | `{{cookiecutter.directory_name}}/CHANGELOG.md` | Empty changelog boilerplate |
| Create | `{{cookiecutter.directory_name}}/LICENSE` | License text with Jinja2 conditionals |
| Rewrite | `{{cookiecutter.directory_name}}/README.md` | Full template with tooling docs, structure, badges |

---

## Chunk 1: Core Configuration & Hooks

### Task 1: Update `cookiecutter.json`

**Files:**
- Modify: `cookiecutter.json`

- [ ] **Step 1: Update cookiecutter.json with new variables and fixes**

Replace the entire file with:

```json
{
    "directory_name": "DS_project",
    "project_name": "default_project",
    "project_description": "default_description",
    "author_name": "Your Name",
    "author_email": "your@email.com",
    "python_version": "3.10",
    "default_branch": "main",
    "license": ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "Proprietary"],
    "keywords": "",
    "include_dvc": "false",
    "python_test_versions": "3.10, 3.11, 3.12"
}
```

Key changes from current:
- `python_version`: `">=3.12"` → `"3.10"` (bare version number)
- `target_python_version`: removed entirely
- Added: `author_name`, `author_email`, `license` (choice list), `keywords`

- [ ] **Step 2: Commit**

```bash
git add cookiecutter.json
git commit -m "feat: update cookiecutter.json with new variables, fix python_version format"
```

---

### Task 2: Create pre-generation hook

**Files:**
- Create: `hooks/pre_gen_project.py`

- [ ] **Step 1: Create hooks directory and pre_gen_project.py**

Create `hooks/pre_gen_project.py` at the cookiecutter root (same level as `cookiecutter.json`):

```python
"""Pre-generation hook: validates cookiecutter inputs before generating the project."""

import sys


def parse_version_tuple(version_str):
    """Parse a version string like '3.10' into a comparable tuple like (3, 10)."""
    try:
        return tuple(int(x) for x in version_str.strip().split("."))
    except ValueError:
        print(f"ERROR: '{version_str}' is not a valid Python version (expected format: X.Y)")
        sys.exit(1)


def validate_python_versions():
    """Ensure all test versions are >= the minimum python_version."""
    python_version = "{{ cookiecutter.python_version }}"
    test_versions_str = "{{ cookiecutter.python_test_versions }}"

    min_version = parse_version_tuple(python_version)
    test_versions = [v.strip() for v in test_versions_str.split(",")]

    for test_ver in test_versions:
        test_tuple = parse_version_tuple(test_ver)
        if test_tuple < min_version:
            print(
                f"ERROR: python_test_versions contains '{test_ver}' "
                f"but python_version is {python_version}.\n"
                f"All test versions must be >= python_version.\n"
                f"Fix: either lower python_version (e.g. {test_ver}) "
                f"or remove versions below the minimum from python_test_versions."
            )
            sys.exit(1)


if __name__ == "__main__":
    validate_python_versions()
```

- [ ] **Step 2: Commit**

```bash
git add hooks/pre_gen_project.py
git commit -m "feat: add pre-generation hook to validate python test versions"
```

---

### Task 3: Create post-generation hook

**Files:**
- Create: `hooks/post_gen_project.py`

- [ ] **Step 1: Create post_gen_project.py**

Create `hooks/post_gen_project.py` at the cookiecutter root:

```python
"""Post-generation hook: replaces {YEAR} placeholder in LICENSE with the current year."""

import datetime
from pathlib import Path


def replace_year_in_license():
    """Replace {YEAR} placeholder in LICENSE file with current year."""
    license_path = Path("LICENSE")
    if license_path.exists():
        content = license_path.read_text()
        content = content.replace("{YEAR}", str(datetime.datetime.now().year))
        license_path.write_text(content)


if __name__ == "__main__":
    replace_year_in_license()
```

- [ ] **Step 2: Commit**

```bash
git add hooks/post_gen_project.py
git commit -m "feat: add post-generation hook for LICENSE year substitution"
```

---

## Chunk 2: Template File Fixes

### Task 4: Fix Dockerfile

**Files:**
- Modify: `{{cookiecutter.directory_name}}/Dockerfile.base`

- [ ] **Step 1: Rewrite Dockerfile.base**

Replace the entire file. Remove the dead first FROM block, use the cleaner `COPY --from` uv install (per spec), parameterize Python version, fix typo:

```dockerfile
# Install uv
FROM python:{{ cookiecutter.python_version }}-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen
```

Changes from current:
- Removed the dead orphaned first FROM block (lines 1-3 of original)
- Replaced the `install.sh` approach (curl + ADD + RUN) with the cleaner `COPY --from=ghcr.io/astral-sh/uv:latest` approach (matches spec)
- Comment: `Intall` → `Install`
- Python version: `3.12` → `{{ cookiecutter.python_version }}`
- Removed `AS base` (single stage, no name needed)
- Removed unnecessary `curl ca-certificates` apt-get install (no longer needed with COPY approach)

- [ ] **Step 2: Commit**

```bash
git add "{{cookiecutter.directory_name}}/Dockerfile.base"
git commit -m "fix: remove dead code from Dockerfile, parameterize Python version"
```

---

### Task 5: Update pyproject.toml

**Files:**
- Modify: `{{cookiecutter.directory_name}}/pyproject.toml`

- [ ] **Step 1: Update existing fields**

In `{{cookiecutter.directory_name}}/pyproject.toml`, make these changes:

Change `requires-python` (line 9) from:
```toml
requires-python = "{{cookiecutter.python_version}}"
```
to:
```toml
requires-python = ">={{cookiecutter.python_version}}"
```

Change `target-version` (line 37) from:
```toml
target-version = "{{cookiecutter.target_python_version}}"
```
to:
```toml
target-version = "py{{ cookiecutter.python_version | replace('.', '') }}"
```

- [ ] **Step 2: Add new metadata fields**

After `requires-python` line and before `dependencies = []`, add:

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

- [ ] **Step 3: Commit**

```bash
git add "{{cookiecutter.directory_name}}/pyproject.toml"
git commit -m "feat: add metadata fields to pyproject.toml, fix version derivations"
```

---

### Task 6: Fix pre-commit config

**Files:**
- Modify: `{{cookiecutter.directory_name}}/.pre-commit-config.yaml`

- [ ] **Step 1: Replace uvx with uv run and update comment**

In `{{cookiecutter.directory_name}}/.pre-commit-config.yaml`, change three lines:

Line 3 (comment) — change:
```yaml
  # Ruff linter and formatter (local, using uvx)
```
to:
```yaml
  # Ruff linter and formatter (local, using uv run)
```

Line 8 — change:
```yaml
        entry: uvx ruff check --fix --exit-non-zero-on-fix
```
to:
```yaml
        entry: uv run ruff check --fix --exit-non-zero-on-fix
```

Line 14 — change:
```yaml
        entry: uvx ruff format
```
to:
```yaml
        entry: uv run ruff format
```

- [ ] **Step 2: Commit**

```bash
git add "{{cookiecutter.directory_name}}/.pre-commit-config.yaml"
git commit -m "fix: use uv run instead of uvx for ruff in pre-commit hooks"
```

---

### Task 6.5: Parameterize Python version in CI workflows

**Files:**
- Modify: `{{cookiecutter.directory_name}}/.github/workflows/ci.yml`
- Modify: `{{cookiecutter.directory_name}}/.github/workflows/release.yml`

- [ ] **Step 1: Fix ci.yml**

In `{{cookiecutter.directory_name}}/.github/workflows/ci.yml`, line 28 — change:
```yaml
      - name: Set up Python
        run: uv python install 3.12
```
to:
```yaml
      - name: Set up Python
        run: uv python install {{ cookiecutter.python_version }}
```

- [ ] **Step 2: Fix release.yml**

In `{{cookiecutter.directory_name}}/.github/workflows/release.yml`, line 38 — change:
```yaml
      - name: Set up Python
        run: uv python install 3.12
```
to:
```yaml
      - name: Set up Python
        run: uv python install {{ cookiecutter.python_version }}
```

- [ ] **Step 3: Commit**

```bash
git add "{{cookiecutter.directory_name}}/.github/workflows/ci.yml" "{{cookiecutter.directory_name}}/.github/workflows/release.yml"
git commit -m "fix: parameterize hardcoded Python 3.12 in CI workflows"
```

---

### Task 7: Add CHANGELOG.md

**Files:**
- Create: `{{cookiecutter.directory_name}}/CHANGELOG.md`

- [ ] **Step 1: Create CHANGELOG.md**

```markdown
# Changelog
```

- [ ] **Step 2: Commit**

```bash
git add "{{cookiecutter.directory_name}}/CHANGELOG.md"
git commit -m "feat: add CHANGELOG.md boilerplate to template"
```

---

## Chunk 3: LICENSE File

### Task 8: Create LICENSE template

**Files:**
- Create: `{{cookiecutter.directory_name}}/LICENSE`

- [ ] **Step 1: Create LICENSE file with conditional license text**

Create `{{cookiecutter.directory_name}}/LICENSE` with Jinja2 conditionals for each license type. The `{YEAR}` placeholder will be replaced by the post-gen hook at generation time.

```
{%- if cookiecutter.license == "MIT" -%}
MIT License

Copyright (c) {YEAR} {{ cookiecutter.author_name }}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
{%- elif cookiecutter.license == "Apache-2.0" -%}
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work.

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to the Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by the Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding any notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   Copyright {YEAR} {{ cookiecutter.author_name }}

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
{%- elif cookiecutter.license == "GPL-3.0" -%}
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.

  For the complete license text, see <https://www.gnu.org/licenses/gpl-3.0.txt>

Copyright (C) {YEAR} {{ cookiecutter.author_name }}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
{%- elif cookiecutter.license == "BSD-3-Clause" -%}
BSD 3-Clause License

Copyright (c) {YEAR}, {{ cookiecutter.author_name }}

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
{%- elif cookiecutter.license == "Proprietary" -%}
Copyright (c) {YEAR} {{ cookiecutter.author_name }}. All rights reserved.

This software and associated documentation files (the "Software") are
proprietary and confidential. Unauthorized copying, distribution, or use
of this Software, via any medium, is strictly prohibited.
{%- endif %}
```

- [ ] **Step 2: Commit**

```bash
git add "{{cookiecutter.directory_name}}/LICENSE"
git commit -m "feat: add LICENSE template with conditional license text"
```

---

## Chunk 4: README

### Task 9: Rewrite README template

**Files:**
- Rewrite: `{{cookiecutter.directory_name}}/README.md`

- [ ] **Step 1: Write the full README template**

Replace the entire file with:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add "{{cookiecutter.directory_name}}/README.md"
git commit -m "feat: rewrite README with tooling docs, project structure, badges"
```

---

## Chunk 5: Integration Test

### Task 10: Verify template generates correctly

- [ ] **Step 1: Install cookiecutter if not available**

```bash
pip install cookiecutter 2>/dev/null || uv tool install cookiecutter
```

- [ ] **Step 2: Test with default values**

```bash
cd /tmp
cookiecutter --no-input /Users/User/Workspace/Python/MLCookieCutter/.claude/worktrees/heuristic-dhawan
```

Expected: generates `DS_project/` directory without errors.

- [ ] **Step 3: Verify generated files**

Check key files exist and contain correct values:

```bash
cd /tmp/DS_project

# Check python version in pyproject.toml
grep 'requires-python = ">=3.10"' pyproject.toml
grep 'target-version = "py310"' pyproject.toml

# Check metadata
grep 'Your Name' pyproject.toml
grep 'MIT' pyproject.toml

# Check Dockerfile uses correct version
grep 'python:3.10-slim-bookworm' Dockerfile.base

# Check pre-commit uses uv run
grep 'uv run ruff' .pre-commit-config.yaml
grep -c 'uvx' .pre-commit-config.yaml  # should be 0

# Check CI workflows use parameterized python version
grep 'uv python install 3.10' .github/workflows/ci.yml
grep 'uv python install 3.10' .github/workflows/release.yml

# Check LICENSE exists and has current year
cat LICENSE | head -5

# Check CHANGELOG exists
cat CHANGELOG.md

# Check README has content
wc -l README.md  # should be many lines, not 3
```

- [ ] **Step 4: Test with DVC enabled**

```bash
cd /tmp
rm -rf DS_project
cookiecutter --no-input /Users/User/Workspace/Python/MLCookieCutter/.claude/worktrees/heuristic-dhawan include_dvc=true
grep 'DVC' /tmp/DS_project/README.md  # should find DVC section
grep 'dvc' /tmp/DS_project/pyproject.toml  # should find DVC dependencies
```

- [ ] **Step 5: Test pre-gen hook validation (should fail)**

```bash
cd /tmp
rm -rf DS_project
cookiecutter --no-input /Users/User/Workspace/Python/MLCookieCutter/.claude/worktrees/heuristic-dhawan python_version=3.12 python_test_versions="3.10, 3.11, 3.12"
```

Expected: ERROR message about `3.10` being below `3.12`, no project generated.

- [ ] **Step 6: Test with non-default license**

```bash
cd /tmp
rm -rf DS_project
cookiecutter --no-input /Users/User/Workspace/Python/MLCookieCutter/.claude/worktrees/heuristic-dhawan license=BSD-3-Clause
grep 'BSD 3-Clause' /tmp/DS_project/LICENSE
grep 'BSD License' /tmp/DS_project/pyproject.toml
```

- [ ] **Step 7: Clean up and commit any fixes**

```bash
rm -rf /tmp/DS_project
```

If any verification steps failed, fix the template files and re-test before proceeding.

- [ ] **Step 8: Final commit (if fixes were needed)**

```bash
git add -A
git commit -m "fix: address issues found during integration testing"
```
