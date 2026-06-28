# Feature Specs

This folder stores human-written prompts, context, constraints, and designs for
features, fixes, experiments, and one-off implementation tasks.

The developer owns the initial spec. Agents should read the relevant spec before
implementation and should not silently rewrite human context.

## Filename Convention

Use:

```text
YYYY-MM-DD-developer-name-short-feature-name.md
```

Example:

```text
2026-06-27-anton-persistent-memory.md
```

## Editing Rules

- Human-authored content is the review priority.
- Agent additions to a human-authored spec must be written in *italics*.
- Agent removals or reversals of human-authored content must use
  ~~strikethrough~~.
- If important behavior is underspecified, ask the developer to add human
  context or add an explicitly marked agent amendment.

## Spec Template

```markdown
# Feature Spec - Feature Name

Developer: Name
Date: YYYY-MM-DD
Status: Draft | Ready for implementation | Implemented | Superseded
Related PRs: Link or branch name

## Problem

Describe the user, business, research, or operational problem.

## Goals

- State the behavior or outcome that must exist after implementation.

## Non-Goals

- State what this task intentionally does not solve.

## Context and Constraints

- Include product assumptions, model/data assumptions, deployment constraints,
  latency/cost constraints, compliance constraints, hardware constraints, and
  compatibility requirements.

## Design

Describe the intended approach, key components, data flow, and major tradeoffs.

## Testing and Evaluation

- Unit tests:
- Integration or smoke tests:
- Regression tests:
- Stress or load tests:
- Experiment/evaluation metrics:

## Review Notes

- List the docs reviewers should inspect with this PR.

## Agent Amendments

*Agents may add clarifications here in italics after developer approval or when
recording implementation-specific discoveries.*
```
