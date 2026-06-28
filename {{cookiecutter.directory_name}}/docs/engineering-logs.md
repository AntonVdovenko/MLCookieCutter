# Engineering Logs

Timestamped, implementation-specific context for `{{ cookiecutter.project_name }}`.
Use this as the first line of defense for debugging setup, runtime, dependency,
hardware, deployment, dataset, and experiment issues. Newest entries go first.

Agents must update this file when they make changes that future humans or agents
may need to understand. Examples include dependency or environment updates,
CUDA/device changes, switching between Docker and bare-metal execution, Helm or
Kubernetes changes, local deployment smoke-test changes, dataset regeneration,
and experiment config changes.

## Entry Format

```markdown
## YYYY-MM-DDTHH:MM:SS+TZ - Short title

Author/Agent: Name or tool
Scope: Files, configs, datasets, deployment, or experiment touched

Context:
- Why this change was made.

Changes:
- What changed.

Validation:
- Commands, smoke tests, benchmark runs, or manual checks and their results.

Follow-ups:
- Risks, open questions, cleanup, or next steps.
```

---

## {GENERATION_DATE} - Project scaffold generated

Author/Agent: Cookiecutter
Scope: Initial repository scaffold

Context:
- Generated `{{ cookiecutter.project_name }}` from the ML cookiecutter template.

Changes:
- Created baseline Python project structure, tooling config, starter docs, and
  agent workflow instructions.

Validation:
- Run `make init_project`, `uv run pytest`, and `uv run ruff check .` after the
  first commit to validate the generated project in its target environment.

Follow-ups:
- Add project-specific setup notes, feature specs, architecture/API details, and
  experiment context before the first implementation PR.
