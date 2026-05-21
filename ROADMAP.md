# ROADMAP

## Current Target

Current version: v0.1.0
Theme: Lee-only minimal auditable scaffold

This roadmap intentionally contains only the current initial version. Future versions will be planned only after human review of v0.1.0 outputs, data gaps, and implementation limitations.

## v0.1.0 Goals

Build the smallest Python project that can represent the Lee 2020 He APPJ CR-model reproduction workflow using only data explicitly available from Lee 2020 or manually marked seed data.

The purpose of v0.1.0 is not full quantitative reproduction. The purpose is to establish a clean, auditable, config-driven, provenance-safe foundation.

## In Scope

- Python package scaffold.
- Root `AGENTS.md`.
- `.agents/ROUTER.md` and module-level agent rules.
- `docs/devlog/` development feedback files.
- Data schema and config schema.
- Data layering with `data/raw_sources`, `data/staged`, and `data/canonical`.
- `n <= 5` LS-term helium level definitions.
- Lee 2020 Table I/II records that can be clearly read.
- Disabled placeholders for OCR-uncertain or primary-source-required data.
- Four target He spectral-line seed records.
- Minimal model, rates, solver, spectra, fit, harness, and CLI interfaces.
- Data audit tests and basic numerical sanity tests.

## Out Of Scope

- NIST/LXCat data fetching.
- Importing or verifying data from Lee-cited primary sources.
- Full quantitative reproduction of Lee 2020.
- Air chemistry.
- J-resolved fine structure.
- Treating `He2+` or `He2*` as fitted variables.
- Enabling unverified, OCR-uncertain, or estimated scientific data by default.

## Acceptance Criteria

- `pytest` passes.
- `he-cr list-levels` lists all `n <= 5` LS-term levels.
- `he-cr list-reactions --all` lists source, unit, review status, and enabled status.
- Unverified data is disabled by default.
- Unit validation catches unclear or inconsistent units.
- Data audit flags OCR-uncertain or source-incomplete records.
- Basic spectrum command can report four target seed lines or explicitly identify missing verified transition data.
- Basic scan harness can run only with verified enabled data or fail closed with a clear missing-data report.
- `docs/devlog/HANDOFF.md` records current status, known blockers, and recommended next step.

## Future Versions

Future versions are intentionally not specified here.

They must be planned only after human review of:

- v0.1.0 outputs;
- missing data records;
- solver limitations;
- failed tests or known numerical issues;
- external data acquisition feasibility.
