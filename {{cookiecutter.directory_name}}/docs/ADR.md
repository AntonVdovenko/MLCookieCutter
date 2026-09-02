# Architecture Decision Records

Architecture decision records (ADRs) for `{{ cookiecutter.project_name }}`: one
entry per significant technical decision — what was chosen, the context that
forced the choice, and the consequences accepted with it. The engineering log
records *what was implemented and how*; the feature spec records *what was
asked for*; this file records *why the architecture is the way it is*, so a
future reader does not have to reconstruct the reasoning from log entries,
spec strikethroughs, and PR bodies.

## Rules

- **One entry per decision.** Numbered `ADR-NNNN` in the order the decisions
  were made, oldest first, with the index below kept in sync.
- **What qualifies.** Structural choices (module boundaries, service or
  package layout, the configuration model), public-contract choices (API
  shape, data formats, versioning and declaration policy), default runtime
  behavior that consumers or experiments depend on (default models,
  thresholds, configuration defaults), tooling or dependency choices with
  lasting effect, and any reversal of a recorded decision. Bug fixes,
  parameter retunes, refactors that preserve an existing decision, and
  documentation wording do not qualify — they belong in the engineering log
  only.
- **Accepted entries are immutable.** Never rewrite the Context, Decision, or
  Consequences of an Accepted entry. To change course, add a new entry that
  says what it replaces and why, and change only the old entry's Status line
  to `Superseded by ADR-NNNN`. An entry that extends a prior one without
  reversing it cites the prior entry in its Context and leaves the prior
  entry's Status untouched.
- **Status values.** `Proposed` (drafted, awaiting the developer's decision),
  `Accepted`, `Superseded by ADR-NNNN`, `Deprecated` (no longer applies and
  nothing replaced it).
- **Who decides.** The developer owns decisions. An agent writes an entry as
  `Accepted` only when the developer made or explicitly approved the decision
  (in a feature spec, in review, or in the session); otherwise the entry is
  `Proposed` and the PR asks the developer to accept it.
- **Keep it short.** An entry is the decision and its reasoning, not the
  implementation. Link the spec, engineering-log entry, or PR that carries
  the detail under Sources.
- **Same PR.** Work that introduces, changes, or reverses a qualifying
  decision adds its ADR entry in the same PR, and the matching engineering-log
  entry cites the ADR number.

## Entry Format

```markdown
## ADR-NNNN - Short imperative title

Date: YYYY-MM-DD
Status: Proposed | Accepted | Superseded by ADR-NNNN | Deprecated
Deciders: Who made the call

### Context

The forces at play: the problem, the constraints, what made a decision
necessary.

### Decision

What was chosen, stated plainly.

### Consequences

What becomes easier, what becomes harder, what the team accepts as a
trade-off.

### Sources

- Spec, engineering-log entry, PR, or report that carries the detail.
```

## Index

| ADR | Title | Date | Status |
| --- | --- | --- | --- |
| ADR-0001 | Adopt the template tooling baseline | {GENERATION_DAY} | Accepted |

---

## ADR-0001 - Adopt the template tooling baseline

Date: {GENERATION_DAY}
Status: Accepted
Deciders: {{ cookiecutter.author_name }}

### Context

`{{ cookiecutter.project_name }}` was generated from the MLCookieCutter
template, which bundles tooling decisions that shape every later change: how
dependencies are locked, how versions are minted and released, how commits are
validated, and which documents humans and agents keep current.

### Decision

- Dependencies and environments are managed by uv (`pyproject.toml` plus
  `uv.lock`); ruff lints and formats; pytest runs the tests.
- The package version is derived from git tags by hatch-vcs. The installed
  dist metadata is the only version channel — no version string is rewritten
  in source files.
- Versions are minted automatically by python-semantic-release from
  conventional commits on `{{ cookiecutter.default_branch }}`: `feat` bumps
  minor, `fix` bumps patch. A MAJOR bump is a human decision made through an
  explicit `BREAKING CHANGE` commit. The release workflow creates the release
  commit and tag once and never moves the tag; `uv.lock` is refreshed in a
  follow-up commit.
- Pre-commit hooks enforce formatting and conventional commit messages.
- `docs/ENGINEERING_LOGS.md`, `docs/ADR.md`, and `docs/feature-specs/` are
  kept current as part of feature work, as described in `CLAUDE.md` and
  `AGENTS.md`.

### Consequences

- No manual version bumps and no hand-maintained changelog; a tag is a stable
  identifier of what was released, and release history follows from commit
  messages.
- Commit messages must follow the conventional format or the local hook
  rejects the commit.
- Replacing any of these tools is itself a recorded decision: add a new ADR
  that supersedes this one instead of editing it.

### Sources

- `README.md` (Tooling, GitHub Actions)
- `.github/workflows/release.yml` and `pyproject.toml`
  (`[tool.semantic_release]`)
- `docs/ENGINEERING_LOGS.md` — "Project scaffold generated" entry
