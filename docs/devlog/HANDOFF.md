# Handoff

This is the first file a future agent should read after `AGENTS.md`, `ROADMAP.md`, and `.agents/ROUTER.md`.

## Current Target

Version: v0.1.0

Theme: Lee-only minimal auditable scaffold.

Rule: do not add unverified external data in v0.1.0. Future versions are intentionally not planned until human review.

## Required Reading Order For Next Agent

1. `AGENTS.md`
2. `ROADMAP.md`
3. `.agents/ROUTER.md`
4. Relevant module rule under `.agents/rules/`
5. For issue work, `docs/devlog/AGENT_ISSUE_ROUTER.md`
6. For issue work, `docs/devlog/issue_dependencies.yaml`
7. `docs/devlog/DECISIONS.md`
8. If changing scientific claims or reports, also read `docs/devlog/KNOWN_LIMITATIONS.md`

## Current Project State

The initial scaffold exists and tests pass.

Core files:

- Package: `src/he_cr_model/`
- Data: `data/raw_sources/`, `data/staged/`, `data/canonical/`
- Schemas: `schemas/`
- Config seed: `configs/lee2020_minimal_scan.json`
- Tests: `tests/`
- Devlog: `docs/devlog/`

## What Works

- `n <= 5` LS-term He levels are defined in `src/he_cr_model/levels.py`.
- Lee Table II AI rates are entered in `data/canonical/lee2020_table_ii_ai.json`.
- A small Lee Table I subset is entered in `data/staged/lee2020_table_i.json`.
- A complete non-canonical Lee Table I reference index is entered in `data/staged/lee2020_table_i_reference.json`.
- Four Lee target spectral lines are seeded in `data/staged/spectral_lines_seed.json`.
- CLI can list levels and reactions.
- Tests pass.

Verification command:

```powershell
python -m pytest
```

Last verified result: `11 passed`.

## Intentional Fail-Closed Behavior

These commands are expected to report missing data rather than produce fake results:

```powershell
$env:PYTHONPATH='src'
python -m he_cr_model.cli spectrum
python -m he_cr_model.cli scan
python -m he_cr_model.cli audit-data
```

Why:

- `spectrum` fails closed because `data/staged/spectral_lines_seed.json` lacks verified Einstein `A` coefficients.
- `scan` fails closed because verified electron-impact source terms are not included in v0.1.0.
- `audit-data` flags `LEE2020_T1_R23_OCR_CHECK` because its rate expression/unit require original-table review.

## Open Issues To Check First

Agent issue router is in `docs/devlog/AGENT_ISSUE_ROUTER.md`.

Compact dependency status is in `docs/devlog/issue_dependencies.yaml`.

Detailed human-readable issue cards are in `docs/devlog/ACTIVE_ISSUES.md`.

Visual issue dashboard:

- `docs/devlog/ISSUE_DASHBOARD.md`

High-priority issues:

- ISSUE-001: He I levels and spontaneous-radiation data must be built from NIST ASD.
- ISSUE-002: Lee Table I reaction 20 excited-state branch is a disabled placeholder.
- ISSUE-003: Lee Table I multi-channel reaction completeness is not fully audited.
- ISSUE-004: electron-impact source data is missing from v0.1.0.
- ISSUE-005: Lee Table I reaction 23 OCR/units unreliable.
- ISSUE-006: Lee Table I reaction 6 must expand to concrete Table II AI channels.
- ISSUE-007: Lee Table I reaction 9 unit ambiguity.
- ISSUE-008: project-wide species, variable, and unit convention is missing.
- ISSUE-009: reaction stoichiometry parsing and CR source/loss assembly is not implemented.

## Current Guardrails

- Do not enable any record whose `review_status` is not `verified_from_lee2020`.
- Do not invent or estimate missing rates, cross sections, or Einstein `A` coefficients.
- Preserve original paper reaction numbering with `original_reaction_no` and `channel_id` for Table I records.
- If adding a Table I reaction, check whether the original reaction number has multiple product channels.
- Keep internal `Te` as eV and `Tg` as K unless a future unit/species convention document defines explicit conversion handling.
- Do not evaluate rate expressions with ambiguous `Te` units.
- Do not claim the solver builds full CR source/loss equations; currently it only has an AI-loss sanity helper.
- If a finding affects future work, update `docs/devlog/AGENT_ISSUE_ROUTER.md`, `docs/devlog/issue_dependencies.yaml`, and `docs/devlog/ACTIVE_ISSUES.md` as needed.

## Recommended Next Task

Create a project-wide unit/species convention document, then add structured reaction fields for reactants/products so future solver work can assemble source/loss terms safely.
