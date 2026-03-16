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
