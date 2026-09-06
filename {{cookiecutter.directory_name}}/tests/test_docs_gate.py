"""The pre-PR hook: code changes do not reach a pull request without a docs pass."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".claude" / "hooks" / "docs_gate.py"
PR = 'gh pr create --title "x" --body-file - <<EOF\nbody\nEOF'


def _gate():
    spec = importlib.util.spec_from_file_location("docs_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_commands_that_do_not_open_a_pull_request_pass():
    assert _gate().verdict("git push -u origin feat/x", ["src/rail_llm_judge/judge.py"]) is None


def test_docs_only_change_passes():
    assert _gate().verdict(PR, ["docs/ADR.md", "README.md"]) is None


def test_code_change_without_docs_is_refused_and_names_what_changed():
    message = _gate().verdict(PR, ["src/rail_llm_judge/judge.py", "docs/ENGINEERING_LOGS.md"])
    assert message is not None
    assert "API_DOCUMENTATION" in message and "judge.py" in message and "DOCS_REVIEWED=1" in message


def test_code_change_with_a_doc_touched_passes():
    changed = [
        "src/rail_llm_judge/judge.py",
        "docs/API_DOCUMENTATION.md",
        "docs/ENGINEERING_LOGS.md",
    ]
    assert _gate().verdict(PR, changed) is None


def test_code_change_without_an_engineering_log_entry_is_refused():
    message = _gate().verdict(PR, ["scripts/calibration/run_agreement.py", "README.md"])
    assert message is not None and "ENGINEERING_LOGS" in message


def test_the_review_marker_lets_the_pull_request_through():
    assert _gate().verdict("DOCS_REVIEWED=1 " + PR, ["src/rail_llm_judge/judge.py"]) is None


def _git(cwd: Path, *args: str) -> str:
    env = {
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        env={**env, "PATH": os.environ["PATH"]},
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def test_hook_reads_the_branch_diff_and_blocks_with_exit_code_2(tmp_path: Path):
    _git(tmp_path, "init", "-q", "-b", "{{ cookiecutter.default_branch }}")
    (tmp_path / "README.md").write_text("readme\n")
    _git(tmp_path, "add", "."), _git(tmp_path, "commit", "-qm", "init")
    _git(tmp_path, "checkout", "-qb", "feat/x")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "thing.py").write_text("x = 1\n")
    _git(tmp_path, "add", "."), _git(tmp_path, "commit", "-qm", "feat: thing")
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": PR}})
    run = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=tmp_path,
        input=payload,
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 2, run.stderr
    assert "src/thing.py" in run.stderr
    passing = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=tmp_path,
        input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status"}}),
        capture_output=True,
        text=True,
        check=False,
    )
    assert passing.returncode == 0
