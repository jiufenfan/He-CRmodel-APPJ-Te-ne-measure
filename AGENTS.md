# AGENTS.md

## Project Principle

This is a literature-reproduction scientific computing project. Prefer auditable, reproducible scientific workflow over merely runnable code.

Do not fabricate reaction rates, cross sections, level energies, wavelengths, Einstein A coefficients, fitting parameters, or benchmark values.

Every scientific datum must come from Lee 2020, a primary reference cited by Lee 2020, an authoritative database, a documented scraping or digitization workflow, or user-provided data.

If a value cannot be sourced, mark it as `MISSING`, `TODO_SOURCE`, or `needs_primary_source_check`. Do not invent plausible values. Unverified data must be disabled by default.

When entering reaction data, check completeness against the original paper numbering. If one original reaction number contains multiple product channels, represent every channel as a separate record or a disabled placeholder that requires human review.

## Roadmap Workflow

Before making changes, read `ROADMAP.md`.

Only implement the current version scope.

Do not add future-version features unless the user explicitly approves a roadmap update.

Future versions must not be planned in detail until human review is complete.

If a requested change expands scope, update `docs/devlog/DECISIONS.md` and ask whether `ROADMAP.md` should be revised.

## Development Feedback Workflow

Before changing code, read `.agents/ROUTER.md`, the relevant module rule, `docs/devlog/HANDOFF.md`, and `docs/devlog/ACTIVE_ISSUES.md`.

Before working on a GitHub issue or multi-agent task, also read `docs/devlog/ISSUE_DEPENDENCY_GRAPH.md` and verify that the issue is not blocked.

If fixing an error, also read `docs/devlog/ERROR_LOG.md`.

When a command fails in a way that affects future work, summarize it in `docs/devlog/ERROR_LOG.md`.

Generated outputs are not canonical memory. Promote important findings into `docs/devlog/`.

## Multi-Agent Workflow

Agents must not work directly on `main`. Each agent must use a dedicated issue branch named `codex/issue-XXX-short-name`.

If the user asks to solve, fix, implement, continue, review, or work on a GitHub issue number or local issue ID, enter issue-work mode automatically.

Issue implementation branches must not modify governance or rule files by default.

This includes:

- `AGENTS.md`
- `.agents/ROUTER.md`
- `.agents/rules/`
- `docs/devlog/ISSUE_DEPENDENCY_GRAPH.md`

These files may be changed only when:

1. the user explicitly asks for a rule or process update; or
2. the issue itself is a governance or rule issue.

If an agent discovers a rule gap while working on another issue, it must report the gap and ask for a separate rule update instead of modifying governance files inside the current issue branch.

Issue-work mode requires identifying the issue, checking `docs/devlog/ISSUE_DEPENDENCY_GRAPH.md`, stating dependency status, recommending the model, defining the branch name, and defining allowed read/write file scope before implementation.

Before starting issue work, an agent must check `docs/devlog/ISSUE_DEPENDENCY_GRAPH.md`. If the issue is blocked, the agent may only work on explicitly allowed documentation, schema, placeholder, test, or fail-closed behavior.

Do not start solver or quantitative model work before required data, unit, and provenance issues are unblocked.

Do not promote data from `data/raw_sources/` or `data/staged/` into `data/canonical/` without explicit human review evidence.

Pull requests must reference the GitHub issue they address. Scientific data and model changes require human review before merge.

Sub-agent tasks must be scoped narrowly. Do not ask a sub-agent to inspect or refactor the whole repository by default.

When assigning a sub-agent, specify the GitHub issue, branch name, files to read first, files it may modify, and tests to run. Prefer passing concrete local `pytest` failures to the sub-agent over asking it to guess failures through broad exploration.

## Configuration And Data Rules

Paper parameters, scan ranges, enabled reactions, fitting options, and physical assumptions must come from config files.

Data is separated into `data/raw_sources/`, `data/staged/`, and `data/canonical/`. Raw sources are source-nearest material, staged data is extracted but not fully verified, and canonical data is human-reviewed data allowed for default use.

Do not hard-code paper-specific scientific parameters inside model functions.

Configs must be schema-checked. Missing critical config should fail closed.

Scientific defaults must be explicit in config and included in run reports.

## Unit And Dimension Safety

Use `cm^-3` for densities by default. Use `cm^3/s` for two-body reactions and `cm^6/s` for three-body reactions.

Use `eV` for electron temperature and `K` for gas temperature.

For formulas involving `Tg/Te`, explicitly document whether `Te` must be converted to Kelvin.

Unknown or inconsistent units must fail validation or remain disabled.

## Separation Of Concerns

Data layer stores data and provenance only.

Model layer performs pure computation only.

Config layer defines assumptions and parameter choices.

Harness layer loads config/data, calls the model, saves outputs, and generates reports.

The model layer must not read YAML/CSV, write files, plot figures, or contain paper-specific reproduction logic.

## Testing And Regression

Tests must cover level completeness, target spectral-line mapping, unverified-data disabling, reaction unit consistency, non-negative outputs, expected AI effect direction, and fixed-config regression behavior.
