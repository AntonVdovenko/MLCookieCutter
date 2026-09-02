import json
import re
import tomllib
from pathlib import Path

import pytest
from cookiecutter.exceptions import FailedHookException
from cookiecutter.main import cookiecutter


TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PYTHON_TEST_VERSIONS = "3.10, 3.11, 3.12, 3.13, 3.14"


def render_template(tmp_path: Path, **extra_context: str) -> Path:
    config_file = tmp_path / "cookiecutter.yaml"
    config_file.write_text(
        "\n".join(
            [
                f"cookiecutters_dir: {tmp_path / 'cookiecutters'}",
                f"replay_dir: {tmp_path / 'replay'}",
            ]
        )
    )

    context = {
        "directory_name": "HighViewPower",
        "project_name": "high-view-power-interview",
        "project_description": "Interview project",
        "author_name": "Test Author",
        "author_email": "test@example.com",
        "python_version": "3.12",
        "default_branch": "main",
        "license": "MIT",
        "keywords": "",
        "include_dvc": "false",
        "python_test_versions": "3.12",
    }
    context.update(extra_context)

    return Path(
        cookiecutter(
            str(TEMPLATE_ROOT),
            no_input=True,
            output_dir=tmp_path,
            config_file=str(config_file),
            extra_context=context,
        )
    )


def test_template_creates_importable_package_layout(tmp_path: Path) -> None:
    generated = render_template(tmp_path)
    package_dir = generated / "src" / "high_view_power_interview"

    assert package_dir.is_dir()
    assert (package_dir / "__init__.py").is_file()
    assert not (generated / "src" / "__init__.py").exists()

    pyproject = (generated / "pyproject.toml").read_text()
    assert 'packages = ["src/high_view_power_interview"]' in pyproject
    assert 'known-first-party = ["high_view_power_interview"]' in pyproject

    smoke_test = (generated / "tests" / "test_package.py").read_text()
    assert "import high_view_power_interview" in smoke_test


def test_default_python_test_matrix_tracks_current_stable_versions() -> None:
    cookiecutter_config = json.loads((TEMPLATE_ROOT / "cookiecutter.json").read_text())

    assert cookiecutter_config["python_test_versions"] == DEFAULT_PYTHON_TEST_VERSIONS

    readme = (TEMPLATE_ROOT / "README.md").read_text()
    assert "| `python_test_versions` |" in readme
    assert f"| `{DEFAULT_PYTHON_TEST_VERSIONS}` |" in readme


def test_template_renders_current_stable_python_test_matrix(tmp_path: Path) -> None:
    generated = render_template(
        tmp_path,
        python_version="3.10",
        python_test_versions=DEFAULT_PYTHON_TEST_VERSIONS,
    )

    ci_workflow = (generated / ".github" / "workflows" / "ci.yml").read_text()
    pyproject = (generated / "pyproject.toml").read_text()
    project_readme = (generated / "README.md").read_text()

    for version in ["3.10", "3.11", "3.12", "3.13", "3.14"]:
        assert f'"{version}"' in ci_workflow
        assert f"Programming Language :: Python :: {version}" in pyproject

    assert DEFAULT_PYTHON_TEST_VERSIONS in project_readme


def test_template_renders_python_test_matrix_with_or_without_spaces(tmp_path: Path) -> None:
    generated = render_template(tmp_path, python_test_versions="3.12,3.13")

    ci_workflow = (generated / ".github" / "workflows" / "ci.yml").read_text()
    assert '          "3.12",' in ci_workflow
    assert '          "3.13"' in ci_workflow
    assert "3.12,3.13" not in ci_workflow


def test_template_trims_python_test_matrix_entries(tmp_path: Path) -> None:
    generated = render_template(tmp_path, python_test_versions=" 3.12 , 3.13 ")

    ci_workflow = (generated / ".github" / "workflows" / "ci.yml").read_text()
    assert '          "3.12",' in ci_workflow
    assert '          "3.13"' in ci_workflow


def test_template_rejects_invalid_package_name(tmp_path: Path) -> None:
    with pytest.raises(FailedHookException):
        render_template(tmp_path, package_name="invalid-package-name")


def test_ci_workflow_included_by_default(tmp_path: Path) -> None:
    generated = render_template(tmp_path)

    assert (generated / ".github" / "workflows" / "ci.yml").is_file()
    assert (generated / ".github" / "workflows" / "release.yml").is_file()

    readme = (generated / "README.md").read_text()
    assert "actions/workflows/ci.yml/badge.svg" in readme
    assert "### `ci.yml`" in readme


def test_ci_workflow_excluded_when_disabled(tmp_path: Path) -> None:
    generated = render_template(tmp_path, include_ci="false")

    assert not (generated / ".github" / "workflows" / "ci.yml").exists()
    # Semantic-release versioning is always kept — include_ci only gates the PR pipeline.
    assert (generated / ".github" / "workflows" / "release.yml").is_file()

    readme = (generated / "README.md").read_text()
    assert "actions/workflows/ci.yml/badge.svg" not in readme
    assert "### `ci.yml`" not in readme
    assert "### `release.yml`" in readme


FULL_DOCS_ONLY_NAMES = [
    "SETUP_AND_TESTING_GUIDE.md",
    "DATASET.md",
    "EXPERIMENTS.md",
    "STATUS.md",
    "EVALUATION_AND_FINDINGS.md",
]

MINIMAL_DOCS_NAMES = [
    "ENGINEERING_LOGS.md",
    "ADR.md",
    "C4_ARCHITECTURE.md",
    "API_DOCUMENTATION.md",
]


def test_minimal_docs_set_is_default(tmp_path: Path) -> None:
    generated = render_template(tmp_path)
    docs = generated / "docs"

    for name in MINIMAL_DOCS_NAMES:
        assert (docs / name).is_file()
    for name in FULL_DOCS_ONLY_NAMES:
        assert not (docs / name).exists()
    assert (docs / "feature-specs" / "README.md").is_file()

    readme = (generated / "README.md").read_text()
    assert "SETUP_AND_TESTING_GUIDE" not in readme
    assert "feature-specs" in readme
    for name in ("CLAUDE.md", "AGENTS.md"):
        agent_doc = (generated / name).read_text()
        assert "docs/feature-specs" in agent_doc
        assert "SETUP_AND_TESTING_GUIDE" not in agent_doc
        assert "## Experiment Repository Docs" not in agent_doc
        assert "docs/ENGINEERING_LOGS.md" in agent_doc


def test_full_docs_set_keeps_all_docs(tmp_path: Path) -> None:
    generated = render_template(tmp_path, docs_set="full")
    docs = generated / "docs"

    for name in MINIMAL_DOCS_NAMES + FULL_DOCS_ONLY_NAMES:
        assert (docs / name).is_file()
    assert (docs / "feature-specs" / "README.md").is_file()

    readme = (generated / "README.md").read_text()
    assert "SETUP_AND_TESTING_GUIDE" in readme
    assert "feature-specs" in readme
    for name in ("CLAUDE.md", "AGENTS.md"):
        agent_doc = (generated / name).read_text()
        assert "docs/feature-specs" in agent_doc
        assert "## Experiment Repository Docs" in agent_doc


def test_release_workflow_creates_the_tag_once_and_never_moves_it(tmp_path: Path) -> None:
    generated = render_template(tmp_path)

    workflow = (generated / ".github" / "workflows" / "release.yml").read_text()
    commands = "\n".join(
        line for line in workflow.splitlines() if not line.strip().startswith("#")
    )

    # The old amend + force-tag flow moved the tag after the release commit, so
    # pinned consumers got stale cached wheels misreporting their version.
    assert "git tag -f" not in commands
    assert "--amend" not in commands
    assert "uv run semantic-release version --no-push" in commands
    # uv.lock is refreshed AFTER tagging as a separate follow-up commit.
    assert "uv lock --upgrade-package high-view-power-interview" in commands
    assert 'git commit -m "chore: refresh uv.lock for v$VERSION"' in commands
    assert "git push origin main --tags" in commands


def test_semantic_release_uses_dist_metadata_as_the_only_version_channel(tmp_path: Path) -> None:
    generated = render_template(tmp_path)

    pyproject = tomllib.loads((generated / "pyproject.toml").read_text())
    semantic_release = pyproject["tool"]["semantic_release"]

    # version is dynamic (hatch-vcs from the git tag): rewriting a version
    # string in pyproject or __init__ is dead config that can disagree with
    # dist metadata, and a pre-tag build_command only produces a dev wheel.
    assert "version" in pyproject["project"]["dynamic"]
    assert "version_toml" not in semantic_release
    assert "version_variables" not in semantic_release
    assert "build_command" not in semantic_release
    assert semantic_release["tag_format"] == "v{version}"
    assert semantic_release["changelog"]["default_templates"]["changelog_file"] == "CHANGELOG.md"


def test_changelog_carries_the_semantic_release_insertion_marker(tmp_path: Path) -> None:
    generated = render_template(tmp_path)

    changelog = (generated / "CHANGELOG.md").read_text()

    # Without the marker psr's update mode has nowhere to insert and the
    # changelog stays silently empty release after release.
    assert changelog.startswith("# Changelog\n")
    assert "<!-- version list -->" in changelog


def test_package_version_fallback_is_not_a_plausible_release_number(tmp_path: Path) -> None:
    generated = render_template(tmp_path)

    init = (generated / "src" / "high_view_power_interview" / "__init__.py").read_text()

    assert '__version__ = "0.0.0+unknown"' in init
    assert "updated by semantic-release" not in init


def test_adr_document_has_rules_index_and_a_dated_seed_entry(tmp_path: Path) -> None:
    generated = render_template(tmp_path)

    adr = (generated / "docs" / "ADR.md").read_text()

    for heading in ("## Rules", "## Entry Format", "## Index", "## ADR-0001"):
        assert heading in adr
    assert "| ADR-0001 |" in adr
    assert "Deciders: Test Author" in adr
    # The post-generation hook dates the seed entry; no placeholder survives.
    assert "{GENERATION_DAY}" not in adr
    assert re.search(r"^Date: \d{4}-\d{2}-\d{2}$", adr, flags=re.MULTILINE)
    assert "high-view-power-interview" in adr


@pytest.mark.parametrize("docs_set", ["minimal", "full"])
def test_agent_instructions_require_reading_the_adr_and_stay_aligned(
    tmp_path: Path, docs_set: str
) -> None:
    generated = render_template(tmp_path, docs_set=docs_set)

    claude = (generated / "CLAUDE.md").read_text()
    agents = (generated / "AGENTS.md").read_text()

    for doc in (claude, agents):
        assert "Read `docs/ADR.md`" in doc
        assert "### `docs/ADR.md`" in doc
        assert "## Implementation Logging and Decision Records" in doc
    # Only the intro paragraph may differ between the two agent files.
    marker = "## Required Agent Workflow"
    assert claude.split(marker, 1)[1] == agents.split(marker, 1)[1]


@pytest.mark.parametrize("docs_set", ["minimal", "full"])
def test_readme_maps_the_adr_document(tmp_path: Path, docs_set: str) -> None:
    generated = render_template(tmp_path, docs_set=docs_set)

    readme = (generated / "README.md").read_text()

    assert "Read `docs/ADR.md`" in readme
    assert "| `docs/ADR.md` |" in readme


def test_agent_instructions_state_the_versioning_rules(tmp_path: Path) -> None:
    generated = render_template(tmp_path)

    for name in ("CLAUDE.md", "AGENTS.md"):
        doc = (generated / name).read_text()
        assert "## Versioning" in doc
        # Prose is hard-wrapped; compare phrases on whitespace-normalized text.
        prose = " ".join(doc.split())
        # Bumps come only from conventional commits; MAJOR is the owner's call.
        assert "`feat` → minor, `fix` → patch" in prose
        assert "never bump by hand" in prose
        assert "`BREAKING CHANGE`" in prose
        assert "never mark a commit breaking" in prose


def test_agent_planning_artifacts_stay_local(tmp_path: Path) -> None:
    generated = render_template(tmp_path)

    gitignore = (generated / ".gitignore").read_text().splitlines()
    assert "docs/superpowers/" in gitignore
    assert ".superpowers/" in gitignore

    for name in ("CLAUDE.md", "AGENTS.md"):
        prose = " ".join((generated / name).read_text().split())
        assert "`docs/superpowers/`" in prose
        assert "never be committed or force-added" in prose
