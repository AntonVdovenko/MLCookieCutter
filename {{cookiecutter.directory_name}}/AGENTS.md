# AGENTS.md

Instructions for Codex and other terminal coding agents working in this
repository. Claude Code also has `CLAUDE.md`; keep both files aligned when agent
workflow rules change.

## Required Agent Workflow

Before implementing a feature, bug fix, experiment change, deployment change,
or dependency/environment update:

{%- if cookiecutter.docs_set == "full" %}

1. Read `docs/ENGINEERING_LOGS.md`.
2. Read `docs/ADR.md` — the architecture decision records. An `Accepted`
   decision is settled: do not re-litigate it or quietly reverse it in code.
3. Read the relevant files in `docs/feature-specs/`.
4. Read the documentation file that matches the work area:
   - production architecture: `docs/C4_ARCHITECTURE.md`
   - external integration/API behavior: `docs/API_DOCUMENTATION.md`
   - setup, testing, Docker, Kubernetes, smoke tests: `docs/SETUP_AND_TESTING_GUIDE.md`
   - experiment datasets/plans/results: `docs/DATASET.md`,
     `docs/EXPERIMENTS.md`, `docs/STATUS.md`,
     `docs/EVALUATION_AND_FINDINGS.md`

If the current request conflicts with an existing feature spec, an `Accepted`
ADR, an engineering-log entry, or a documented production contract, stop and
ask the developer before changing behavior.
{%- else %}

1. Read `docs/ENGINEERING_LOGS.md`.
2. Read `docs/ADR.md` — the architecture decision records. An `Accepted`
   decision is settled: do not re-litigate it or quietly reverse it in code.
3. Read the relevant files in `docs/feature-specs/`.
4. Read the documentation file that matches the work area:
   - architecture: `docs/C4_ARCHITECTURE.md`
   - external integration/API behavior: `docs/API_DOCUMENTATION.md`

If the current request conflicts with an existing feature spec, an `Accepted`
ADR, an engineering-log entry, or a documented production contract, stop and
ask the developer before changing behavior.
{%- endif %}

## Documentation Standards

Every project generated from this template has a `docs` folder. These documents
are part of the development workflow, not optional afterthoughts.

### `docs/ENGINEERING_LOGS.md`

- Maintains timestamped, implementation-specific context.
- Agents must update it when they make code, config, environment, deployment,
  CUDA/device, dependency, Docker, Kubernetes, Helm, dataset, or experiment
  changes that future debugging may need.
- Use it as the first line of defense when debugging setup, runtime, hardware,
  driver, deployment, or experiment oddities.
- Keep newest entries at the top.

### `docs/ADR.md`

- Architecture decision records: one numbered `ADR-NNNN` entry per
  significant decision — context, decision, consequences, sources — oldest
  first, with an index table at the top.
- Qualifying decisions: structural choices (module boundaries, service or
  package layout, the configuration model), public-contract choices (API
  shape, data formats, versioning and declaration policy), default runtime
  behavior that consumers or experiments depend on, tooling or dependency
  choices with lasting effect, and any reversal of a recorded decision. Bug
  fixes, parameter retunes, refactors that preserve an existing decision, and
  documentation wording do not qualify — they go to the engineering log only.
- `Accepted` entries are immutable. To change course, add a new entry that
  says what it replaces and why, and change only the old entry's Status line
  to `Superseded by ADR-NNNN`. Never rewrite an `Accepted` entry's content.
- Mark an entry `Accepted` only when the developer made or explicitly
  approved the decision (in a spec, in review, or in the session); otherwise
  write it as `Proposed` and ask the developer to accept it in the PR.

### `docs/feature-specs/`

- Stores human-written prompts, context, constraints, and designs for each
  feature, experiment, fix, or task.
- The developer owns the initial spec and should write enough context for an
  agent or reviewer to understand the intent without reconstructing it from
  code.
- Agent additions to a human-authored spec must be in *italics*.
- Agent removals or reversals of human-authored context must use
  ~~strikethrough~~ rather than silent deletion.
- Do not overwrite human design intent. If requirements are missing or unclear,
  ask the developer to update the spec or clearly mark agent-added amendments.

### `docs/C4_ARCHITECTURE.md`

- Mandatory for production services.
- Optional for experiment-only codebases.
- Must include embedded diagrams in Markdown and be updated when topology,
  service boundaries, data flow, deployment shape, or major components change.

### `docs/API_DOCUMENTATION.md`

- Mandatory for production services.
- Should be the only document an external team needs in order to call or
  integrate with the service.
- For experiment-only codebases with no public API, state that explicitly and
  link to the README, setup guide, and experiment docs.

{%- if cookiecutter.docs_set == "full" %}

### `docs/SETUP_AND_TESTING_GUIDE.md`

- Defines local setup, environment variables, Docker usage, Kubernetes or Helm
  deployment flow, smoke tests, rollback notes, unit tests, regression tests,
  stress tests, and evaluation commands.
- It can stay as one file or be split into separate local, Docker, Kubernetes,
  and CLI guides as the project grows.
{%- endif %}

### `README.md`

- Explains what the repository does and how to navigate the documentation.
- Lists related repositories when production, training, evaluation, or data
  repos are split.
{%- if cookiecutter.docs_set == "full" %}
- For experiment and evaluation repos, README changes should follow the same
  human-vs-agent edit conventions as feature specs.

## Experiment Repository Docs

Experiment and evaluation codebases must also maintain:

- `docs/DATASET.md`: dataset names, generation/curation methodology,
  replication steps, rationale, and output paths.
- `docs/EXPERIMENTS.md`: methods, goals, phases, datasets, plans, open
  questions, remarks, drawbacks, and output paths.
- `docs/STATUS.md`: live experiment status such as not started, dataset,
  experiment dev, experiment running, eval running, benched, failed, skipped,
  pending, and brief findings.
- `docs/EVALUATION_AND_FINDINGS.md`: evaluation settings, benchmarks,
  processes, datasets, quantitative and qualitative findings, and result paths.
{%- endif %}

## PR Review Expectations

- PR descriptions may be generated by an agent, but they must point reviewers to
  the docs that should be reviewed.
- Review priority is human-generated specs and context first, then
  agent-generated or agent-edited architecture/API/setup documentation.
- If a key behavior is not specified clearly enough for review, the developer
  should add human context to the relevant spec and the agent should update any
  affected generated docs.

## Implementation Logging and Decision Records

When you complete meaningful implementation work, add an entry to
`docs/ENGINEERING_LOGS.md` with:

- timestamp and short title;
- author or agent name;
- scope;
- changes made;
- reason/context;
- validation commands and results;
- follow-ups or known risks.

When that work introduces, changes, or reverses an architecture decision (see
the `docs/ADR.md` rules above), also add an ADR entry in the same PR and cite
its number from the engineering-log entry. The log records what was built and
how; the ADR records why the decision was made.
