"""Post-generation hook: fills dynamic placeholders in generated projects."""

import datetime
from pathlib import Path

FULL_DOCS_ONLY = (
    Path("docs") / "SETUP_and_TESTING_GUIDE.md",
    Path("docs") / "Dataset.md",
    Path("docs") / "Experiments.md",
    Path("docs") / "STATUS.md",
    Path("docs") / "Evaluation_and_findings.md",
)


def current_timestamp():
    """Return the local ISO timestamp used in generated documentation."""
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def replace_year_in_license():
    """Replace {YEAR} placeholder in LICENSE file with current year."""
    license_path = Path("LICENSE")
    if license_path.exists():
        content = license_path.read_text()
        content = content.replace("{YEAR}", str(datetime.datetime.now().year))
        license_path.write_text(content)


def replace_generation_date_placeholders():
    """Replace {GENERATION_DATE} placeholders in generated documentation."""
    generation_date = current_timestamp()
    for path in (Path("docs") / "engineering-logs.md",):
        if path.exists():
            content = path.read_text()
            content = content.replace("{GENERATION_DATE}", generation_date)
            path.write_text(content)


def remove_full_docs_if_minimal(docs_set="{{ cookiecutter.docs_set }}"):
    """Keep only the minimal docs profile when the project was generated with docs_set=minimal.

    Minimal keeps README.md, docs/engineering-logs.md, docs/feature-specs/,
    docs/C4_ARCHITECTURE.md, and docs/API_DOCUMENTATION.md; full adds the
    setup/testing guide and the experiment docs.
    """
    if docs_set == "full":
        return
    for path in FULL_DOCS_ONLY:
        if path.exists():
            path.unlink()


def remove_ci_workflow_if_disabled(include_ci="{{ cookiecutter.include_ci }}"):
    """Delete the PR CI workflow when the project was generated with include_ci=false.

    release.yml (semantic-release version bumping) is always kept; only the
    lint/test pipeline on pull requests is optional.
    """
    if include_ci == "true":
        return
    ci_path = Path(".github") / "workflows" / "ci.yml"
    if ci_path.exists():
        ci_path.unlink()


if __name__ == "__main__":
    replace_year_in_license()
    replace_generation_date_placeholders()
    remove_ci_workflow_if_disabled()
    remove_full_docs_if_minimal()
