"""Post-generation hook: fills dynamic placeholders in generated projects."""

import datetime
from pathlib import Path


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


if __name__ == "__main__":
    replace_year_in_license()
    replace_generation_date_placeholders()
