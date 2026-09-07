#!/usr/bin/env python3
"""Claude Code PreToolUse hook: no pull request for a code change without a docs pass.

Reads the tool call from stdin. When the command opens a pull request (`gh pr create`)
and the branch changes code (src/, scripts/, pyproject.toml) without touching any of
the living docs (README, API doc, C4 doc) or the engineering log, it exits 2 with a
message naming what changed, which sends the agent back to review the docs. Prefix the
command with `DOCS_REVIEWED=1` after a deliberate review that found nothing to update.
"""

from __future__ import annotations

import json
import subprocess
import sys

CODE_PREFIXES = ("src/", "scripts/", "pyproject.toml")
LIVING_DOCS = ("README.md", "docs/API_DOCUMENTATION.md", "docs/C4_ARCHITECTURE.md")
ENGINEERING_LOG = "docs/ENGINEERING_LOGS.md"
MARKER = "DOCS_REVIEWED=1"


def changed_files(cwd: str | None = None) -> list[str]:
    """Files the branch changes relative to main (what the pull request will contain)."""
    for base in ("origin/{{ cookiecutter.default_branch }}", "{{ cookiecutter.default_branch }}"):
        merge_base = subprocess.run(
            ["git", "merge-base", "HEAD", base],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if merge_base.returncode == 0:
            break
    else:
        return []
    diff = subprocess.run(
        ["git", "diff", "--name-only", merge_base.stdout.strip(), "HEAD"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return diff.stdout.split()


def verdict(command: str, changed: list[str]) -> str | None:
    """None to let the command run, otherwise the message that blocks it."""
    if "gh pr create" not in command or MARKER in command:
        return None
    code = sorted(f for f in changed if f.startswith(CODE_PREFIXES))
    if not code:
        return None
    problems = []
    if not any(f in LIVING_DOCS for f in changed):
        problems.append("none of the living docs changed: " + ", ".join(LIVING_DOCS))
    if ENGINEERING_LOG not in changed:
        problems.append(f"no entry added to {ENGINEERING_LOG}")
    if not problems:
        return None
    return (
        "Docs gate: this branch changes code but the documentation was not reviewed.\n"
        "Code changed:\n  " + "\n  ".join(code) + "\nMissing:\n  " + "\n  ".join(problems) + "\n"
        "Review docs/API_DOCUMENTATION.md (signatures, fields, flags), docs/C4_ARCHITECTURE.md "
        "(modules, data flow) and README.md (behavior, layout, workflow), update what is stale, "
        "add the engineering-log entry, commit, then open the pull request again. If a deliberate "
        f"review found nothing to change, say so in the PR description and prefix the command with "
        f"`{MARKER}`."
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    command = str(payload.get("tool_input", {}).get("command", ""))
    message = verdict(command, changed_files())
    if message is None:
        return 0
    print(message, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
