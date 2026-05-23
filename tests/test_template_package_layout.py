from pathlib import Path

import pytest
from cookiecutter.exceptions import FailedHookException
from cookiecutter.main import cookiecutter


TEMPLATE_ROOT = Path(__file__).resolve().parents[1]


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
    assert (
        'version_variables = ["src/high_view_power_interview/__init__.py:__version__"]'
        in pyproject
    )

    smoke_test = (generated / "tests" / "test_package.py").read_text()
    assert "import high_view_power_interview" in smoke_test


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
