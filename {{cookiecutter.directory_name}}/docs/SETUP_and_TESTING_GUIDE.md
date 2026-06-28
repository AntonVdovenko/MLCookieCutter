# Setup and Testing Guide - {{ cookiecutter.project_name }}

This guide defines local setup, testing behavior, Docker usage, deployment
notes, smoke tests, regression tests, stress tests, and evaluation commands.
Split it into separate local, Docker, Kubernetes, and CLI guides when the file
gets too large.

## Local Setup

Prerequisites:

- Python >= {{ cookiecutter.python_version }}
- `uv`
- Git
- Docker, if container workflows are used

Initialize the generated project:

```bash
make init_project
```

Run the default validation commands:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Environment Variables

| Name | Required | Default | Description |
|---|---|---|---|
| `ENV` | No | `local` | Runtime environment label |

Record environment-specific surprises in `docs/engineering-logs.md`, especially
dependency, CUDA, device, driver, Docker, Kubernetes, or Helm changes.

## Docker

Build the base image:

```bash
docker build -f Dockerfile.base -t {{ cookiecutter.project_name }}:base .
```

Document project-specific run commands here once an application entrypoint,
training job, or evaluation command exists.

## Kubernetes and Helm

For production services, document:

- namespace and release names;
- chart path and values files;
- required secrets and config maps;
- topology and resource requests;
- rollout command;
- smoke tests;
- rollback command;
- log and metrics locations.

Keep deployment experiments and one-off Helm or values changes in
`docs/engineering-logs.md`.

## Unit Tests

Run:

```bash
uv run pytest
```

Document high-value test subsets here as the project grows.

## Regression Tests

Regression tests should name the behavior they protect and link back to the
feature spec or engineering log entry that explains why the behavior matters.

## Stress and Load Tests

Record:

- workload shape;
- data or fixture paths;
- resource limits;
- pass/fail thresholds;
- output paths;
- follow-up findings.

## Evaluation

For experiment and evaluation repos, link evaluation commands and results to:

- `docs/Dataset.md`
- `docs/Experiments.md`
- `docs/STATUS.md`
- `docs/Evaluation_and_findings.md`

## Debugging Checklist

1. Read `docs/engineering-logs.md` for known setup/runtime issues.
2. Read the relevant feature spec in `docs/feature-specs/`.
3. Reproduce with the smallest command or fixture.
4. Record the fix, validation, and remaining risks in `docs/engineering-logs.md`.
