import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from test_template_package_layout import render_template


def test_generated_project_carries_the_docs_guards(tmp_path: Path) -> None:
    generated = render_template(tmp_path)

    settings = json.loads((generated / ".claude" / "settings.json").read_text())
    hook = settings["hooks"]["PreToolUse"][0]
    assert hook["matcher"] == "Bash"
    assert "docs_gate.py" in hook["hooks"][0]["command"]

    gate = (generated / ".claude" / "hooks" / "docs_gate.py").read_text()
    assert '"origin/main", "main"' in gate
    assert "gh pr create" in gate and "DOCS_REVIEWED=1" in gate

    freshness = (generated / "tests" / "test_docs_freshness.py").read_text()
    assert "import high_view_power_interview as package" in freshness
    assert (generated / "tests" / "test_docs_gate.py").is_file()

    gitignore = (generated / ".gitignore").read_text().splitlines()
    assert ".claude/settings.local.json" in gitignore


def test_gate_follows_the_configured_default_branch(tmp_path: Path) -> None:
    generated = render_template(tmp_path, default_branch="master")

    gate = (generated / ".claude" / "hooks" / "docs_gate.py").read_text()
    assert '"origin/master", "master"' in gate
    assert '"init", "-q", "-b", "master"' in (generated / "tests" / "test_docs_gate.py").read_text()


@pytest.mark.parametrize("docs_set", ["minimal", "full"])
def test_agent_instructions_make_documentation_part_of_done(tmp_path: Path, docs_set: str) -> None:
    generated = render_template(tmp_path, docs_set=docs_set)

    for name in ("CLAUDE.md", "AGENTS.md"):
        prose = " ".join((generated / name).read_text().split())
        assert "Documentation is part of done." in prose
        assert "`tests/test_docs_freshness.py`" in prose
        assert "`.claude/hooks/docs_gate.py`" in prose
        assert "`DOCS_REVIEWED=1`" in prose

    readme = (generated / "README.md").read_text()
    assert "`tests/test_docs_freshness.py`" in readme
    assert "├── .claude/" in readme


@pytest.mark.parametrize("docs_set", ["minimal", "full"])
def test_freshness_and_gate_tests_pass_on_a_fresh_project(tmp_path: Path, docs_set: str) -> None:
    generated = render_template(tmp_path, docs_set=docs_set)

    # A fresh project must start green: no signature, path, map or tag check may
    # fail before anyone has written a line of code.
    env = os.environ | {"PYTHONPATH": str(generated / "src")}
    run = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_docs_freshness.py", "tests/test_docs_gate.py"],
        cwd=generated,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
