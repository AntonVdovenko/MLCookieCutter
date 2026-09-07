"""The documentation must describe the code as it is.

These tests turn "stale docs" into a red test run: every signature the API
doc prints in a Python code block matches the real one, every module has a
place in the C4 doc, every path the living docs name exists, the README's
documentation map lists every documentation file, and an install snippet
that pins the release tag is one the release commit rewrites.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import re
import subprocess
from pathlib import Path

import pytest

import {{ cookiecutter.package_name }} as package

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "{{ cookiecutter.package_name }}"
PACKAGE_DIR = ROOT / "src" / PACKAGE_NAME
API_DOC = ROOT / "docs" / "API_DOCUMENTATION.md"
C4_DOC = ROOT / "docs" / "C4_ARCHITECTURE.md"
README = ROOT / "README.md"
PYPROJECT = ROOT / "pyproject.toml"

# Living documents describe the repo as it is now. Historical records (the
# engineering log, ADRs, feature specs) legitimately name old paths.
LIVING_DOCS = (README, ROOT / "CLAUDE.md", ROOT / "AGENTS.md", API_DOC, C4_DOC)


# --- helpers -----------------------------------------------------------------


def _python_blocks(text: str) -> list[str]:
    return re.findall(r"^```python\n(.*?)^```", text, flags=re.S | re.M)


def _strip_comments(block: str) -> str:
    return "\n".join(re.sub(r"(^|\s)#.*$", "", line) for line in block.splitlines())


def _is_usage_example(block: str) -> bool:
    """Usage snippets import things or assign results; signature listings do neither."""
    return bool(re.search(r"^(from|import)\s|^\w+\s*=[^=]", block, flags=re.M))


def _balanced(text: str, start: int) -> tuple[str, int]:
    """Return the text inside the parenthesis opening at ``start`` and the index after it."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] in "([{":
            depth += 1
        elif text[i] in ")]}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i], i + 1
    raise ValueError(f"unbalanced parenthesis at {text[start : start + 40]!r}")


def _split_top_level(text: str) -> list[str]:
    parts, depth, current = [], 0, []
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    parts.append("".join(current))
    return [p.strip() for p in parts if p.strip()]


def _doc_param_names(inner: str) -> tuple[list[str], bool]:
    """Parameter names a documented signature lists, and whether it is abridged (``...``)."""
    names, abridged = [], False
    for piece in _split_top_level(inner):
        if piece in {"*", "/"}:
            continue
        if piece == "...":
            abridged = True
            continue
        name = re.split(r"[:=]", piece, maxsplit=1)[0].strip().lstrip("*")
        if name in {"self", "cls"}:
            continue
        names.append(name)
    return names, abridged


_HEAD = re.compile(
    r"^(?:@classmethod\s*\n|@staticmethod\s*\n)?(?:def\s+)?([A-Za-z_][\w.]*)\s*\(", re.M
)


def _documented_signatures(text: str) -> list[tuple[str, str, list[str], bool]]:
    """(owner from the nearest heading, dotted name, documented params, abridged)."""
    found = []
    for chunk in re.split(r"(?=^#{2,3} )", text, flags=re.M):
        heading = chunk.splitlines()[0] if chunk.startswith("#") else ""
        m = re.search(r"`([A-Z]\w+)`", heading)
        owner = m.group(1) if m else ""
        for block in _python_blocks(chunk):
            if _is_usage_example(block):
                continue
            clean = _strip_comments(block)
            for head in _HEAD.finditer(clean):
                name = head.group(1)
                inner, _ = _balanced(clean, head.end() - 1)
                params, abridged = _doc_param_names(inner)
                found.append((owner, name, params, abridged))
    return found


def _public_modules() -> list[str]:
    return sorted(
        info.name
        for info in pkgutil.iter_modules([str(PACKAGE_DIR)])
        if not info.name.startswith("_")
    )


def _resolve(owner: str, dotted: str):
    """Find the object a documented name refers to, anywhere in the package."""
    candidates = [dotted]
    if owner and "." not in dotted:
        candidates.insert(0, f"{owner}.{dotted}")
    if owner and "." in dotted and dotted[0].islower():
        # `client.call(...)` under the `Client` heading: an instance of the owner
        candidates.insert(0, f"{owner}.{dotted.split('.', 1)[1]}")
    modules = [package] + [
        importlib.import_module(f"{PACKAGE_NAME}.{name}") for name in _public_modules()
    ]
    for candidate in candidates:
        head, *rest = candidate.split(".")
        for module in modules:
            obj = getattr(module, head, None)
            if obj is None:
                continue
            for attr in rest:
                obj = getattr(obj, attr, None)
                if obj is None:
                    break
            else:
                return obj
    return None


def _real_param_names(obj) -> list[str]:
    sig = inspect.signature(obj)
    return [p.name for p in sig.parameters.values() if p.name not in {"self", "cls"}]


def _backticked_paths(text: str) -> list[str]:
    tokens = re.findall(r"`([^`\s]+)`", text)
    paths = []
    for tok in tokens:
        if any(c in tok for c in "<>*{}|$()") or "..." in tok:
            continue
        # a path under a known directory, or a bare code/doc file name (those live in
        # git; bare data file names live elsewhere and are not checked)
        if re.match(
            r"(docs|scripts|src|data|tests|config|models|notebooks|\.github|\.claude)/", tok
        ) or re.fullmatch(r"[\w.-]+\.(py|md|toml)", tok):
            paths.append(tok.rstrip("/").split("#")[0])
    return paths


def _tracked_basenames() -> set[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return {Path(line).name for line in out.stdout.splitlines()}


def _gitignored(rel: str) -> bool:
    """A documented path that is deliberately absent from clones (listed in .gitignore)."""
    ignore = ROOT / ".gitignore"
    if not ignore.exists():
        return False
    lines = {
        line.strip().rstrip("/")
        for line in ignore.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    return rel.rstrip("/") in lines


def _exists(rel: str, basenames: set[str]) -> bool:
    path = ROOT / rel
    if path.exists() or Path(str(path) + ".dvc").exists():
        return True
    if "/" not in rel:
        return rel in basenames
    # a DVC-tracked directory covers everything below it
    parts = Path(rel).parts
    return any(
        Path(str(ROOT / Path(*parts[:i])) + ".dvc").exists() for i in range(1, len(parts))
    )


def _version_variables() -> list[str]:
    """`[tool.semantic_release] version_variables`, read without a TOML parser (3.10-safe)."""
    text = PYPROJECT.read_text()
    section = re.search(r"^\[tool\.semantic_release\]\n(.*?)(?=^\[|\Z)", text, flags=re.S | re.M)
    if section is None:
        return []
    m = re.search(r"^version_variables\s*=\s*\[(.*?)\]", section.group(1), flags=re.S | re.M)
    return re.findall(r'"([^"]+)"', m.group(1)) if m else []


# --- tests -------------------------------------------------------------------


def test_api_doc_signatures_match_the_code():
    problems = []
    for owner, name, params, abridged in _documented_signatures(API_DOC.read_text()):
        obj = _resolve(owner, name)
        if obj is None:
            problems.append(f"{name}: documented but not found in {PACKAGE_NAME}")
            continue
        try:
            real = _real_param_names(obj)
        except (TypeError, ValueError):
            continue  # builtins / C-level callables have no signature
        if abridged:
            unknown = [p for p in params if p not in real]
            if unknown:
                problems.append(f"{name}: documents parameters the code does not have: {unknown}")
        elif params != real:
            problems.append(f"{name}: doc {params} != code {real}")
    assert not problems, "\n".join(problems)


def test_c4_doc_names_every_module():
    text = C4_DOC.read_text()
    missing = [f"{m}.py" for m in _public_modules() if f"{m}.py" not in text]
    assert not missing, f"modules without a place in the C4 doc: {missing}"


@pytest.mark.parametrize("doc", LIVING_DOCS, ids=lambda p: str(p.relative_to(ROOT)))
def test_paths_named_in_living_docs_exist(doc: Path):
    basenames = _tracked_basenames()
    missing = sorted(
        {
            p
            for p in _backticked_paths(doc.read_text())
            if not _exists(p, basenames) and not _gitignored(p)
        }
    )
    assert not missing, f"{doc.relative_to(ROOT)} names paths that do not exist: {missing}"


def test_readme_documentation_map_lists_every_docs_entry():
    text = README.read_text()
    entries = sorted(
        (f"docs/{p.name}" if p.is_file() else f"docs/{p.name}/")
        for p in (ROOT / "docs").iterdir()
        if not p.name.startswith(".") and not _gitignored(f"docs/{p.name}")
    )
    missing = [e for e in entries if f"`{e}`" not in text and f"`{e.rstrip('/')}`" not in text]
    assert not missing, f"README documentation map does not list: {missing}"


def test_install_snippets_that_pin_a_tag_are_rewritten_by_the_release_commit():
    pinned = {
        str(doc.relative_to(ROOT))
        for doc in LIVING_DOCS
        if re.search(r'tag = "v\d+\.\d+\.\d+"', doc.read_text())
    }
    listed, tags = set(), set()
    for entry in _version_variables():
        file, variable, fmt = entry.split(":")
        assert fmt == "tf", f"{entry}: an install tag must use the tag format (tf)"
        listed.add(file)
        matches = re.findall(
            rf'(?<![\w.-]){variable} = "(v\d+\.\d+\.\d+)"', (ROOT / file).read_text()
        )
        assert len(matches) == 1, f'{file}: expected exactly one `{variable} = "vX.Y.Z"`, found {matches}'
        tags.add(matches[0])
    assert len(tags) <= 1, f"install snippets disagree on the tag: {sorted(tags)}"
    assert pinned <= listed, (
        "these docs pin an install tag the release commit will not rewrite: "
        f"{sorted(pinned - listed)} — list them in [tool.semantic_release] "
        'version_variables as "<file>:tag:tf"'
    )
