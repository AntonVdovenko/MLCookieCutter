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
