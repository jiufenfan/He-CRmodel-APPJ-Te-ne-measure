# Active Issues

This file is the concrete open-problem list for the current v0.1.0 scaffold. Each issue must identify where the problem lives, why it matters, which module owns it, and how a future agent should validate changes.

## ISSUE-001 He I levels and spontaneous-radiation data must be built from NIST ASD

Status: open

Problem:

This is one combined data-quality problem affecting both the model level set and Lee Table I reaction 3.

Current `src/he_cr_model/levels.py` generates LS-term labels structurally, but it does not contain NIST-reviewed He I energy levels, term designations, statistical weights, or source metadata. Therefore it is not yet a physically canonical He I level table.

The four Lee 2020 target He lines are also present only as seed line records. Their wavelengths and transition labels are taken from Lee 2020, but the Einstein `A` coefficients are not verified from NIST ASD, Wiese/Fuhr, or another approved source. Therefore the code must not calculate quantitative line intensities from these records.

This issue also blocks Lee Table I reaction 3:

`He(p) -> He(q) + hv`

because reaction 3 requires a set of spontaneous-radiation channels and transition probabilities `A(p,q)` between verified He I levels.

Where:

- Current structural level code: `src/he_cr_model/levels.py`
- Current spectral-line seed data: `data/staged/spectral_lines_seed.json`
- Future raw NIST exports should go under: `data/raw_sources/nist/`
- Future staged NIST extraction should go under: `data/staged/`
- Future canonical reviewed data should go under: `data/canonical/`
- Records: `HE_587_6`, `HE_667_8`, `HE_706_5`, `HE_728_1`
- Code module: `src/he_cr_model/spectra.py`
- Code module: `src/he_cr_model/levels.py`
- Tests: `tests/test_spectra.py`
- Tests: `tests/test_levels.py`

Affected modules:

- `data`: NIST-derived level and transition data must be staged before canonical promotion.
- `levels`: generated LS-term placeholders must eventually be replaced or backed by NIST-reviewed canonical level records.
- `spectra`: `compute_line_intensities` must fail closed if `einstein_a_s` is missing.
- `reactions`: Lee Table I reaction 3 must be represented by spontaneous-radiation channels `He(p) -> He(q) + hv` with verified `A(p,q)`.
- `cli`: `he-cr spectrum` must report missing verified transition data.

Current required behavior:

- Keep `levels.py` structural only; do not add guessed energies or statistical weights.
- Keep all four line records with `review_status: needs_primary_source_check`.
- Keep `enabled_by_default: false`.
- Do not insert guessed `A` coefficients.
- Do not generate reaction 3 channels from selection rules alone without NIST-reviewed transition probabilities.

How to verify:

```powershell
$env:PYTHONPATH='src'
python -m he_cr_model.cli spectrum
python -m pytest tests/test_levels.py
python -m pytest tests/test_spectra.py
```

Expected result:

- `spectrum` lists all four lines and reports `missing_verified_transition_data`.
- `levels.py` tests only validate structural v0.1.0 placeholders, not canonical NIST energies.
- `tests/test_spectra.py` passes.

Resolution criteria:

- Human exports or otherwise records NIST ASD He I level data into `data/raw_sources/nist/`, with query parameters and ASD version/citation.
- Human stages parsed NIST level data with level id, term label, energy, unit, statistical weight if available, source, query details, and review status.
- Human stages parsed NIST line data with upper/lower level mapping, wavelength, `Aki`/Einstein `A`, accuracy if available, source, query details, and review status.
- Human promotes reviewed records to `data/canonical/`.
- Only canonical reviewed transition records may enable spectrum intensity calculations or Lee reaction 3 spontaneous-radiation channels.

## ISSUE-002 Lee Table I reaction 20 excited-state branch needs primary-source review

Status: open

Problem:

Lee 2020 Table I reaction 20 contains two product channels:

- `He2+ + e- -> 2He`
- `He2+ + e- -> He + He(p)`

The v0.1.0 data now represents both channels, but the second branch has no branch-resolved rate in the parsed text. It is therefore included only as a disabled placeholder requiring human review.

Where:

- Data file: `data/staged/lee2020_table_i.json`
- Verified ground channel: `LEE2020_T1_R20_GROUND`
- Placeholder excited channel: `LEE2020_T1_R20_EXCITED_PLACEHOLDER`
- Code module: `src/he_cr_model/validation.py`
- Tests: `tests/test_reaction_audit.py`

Affected modules:

- `data`: Table I reaction records must preserve original reaction numbering and channel ids.
- `validation`: Table I records should include `original_reaction_no` and `channel_id`.
- `solver`: this DR branch is not enabled in v0.1.0.

Current required behavior:

- Keep `LEE2020_T1_R20_EXCITED_PLACEHOLDER` disabled.
- Keep `review_status: needs_primary_source_check`.
- Do not infer a branch rate from the ground-channel rate.

How to verify:

```powershell
$env:PYTHONPATH='src'
python -m he_cr_model.cli list-reactions --all
python -m pytest tests/test_reaction_audit.py
```

Expected result:

- Reaction 20 appears as two records.
- The excited branch is disabled and unverified.
- Tests confirm both channels are represented.

Resolution criteria:

- Human review determines whether Lee 2020, Royal/Orel, or another cited source provides a branch-resolved rate or cross-section workflow.

## ISSUE-003 Lee Table I multi-channel reaction completeness not fully audited

Status: open

Problem:

Reaction 20 exposed a general data-entry risk: one Lee Table I reaction number may include multiple channels under the same number. A complete staged reference index now exists, but it is not canonical. It must be manually audited against the original Lee Table I before any individual record is promoted or used quantitatively.

Where:

- Source to compare: original Lee 2020 Table I in the PDF/parsed paper directory.
- Complete staged reference index: `data/staged/lee2020_table_i_reference.json`
- Smaller working subset: `data/staged/lee2020_table_i.json`
- Rule file: `.agents/rules/data-agent.md`
- Validation module: `src/he_cr_model/validation.py`

Affected modules:

- `data`: every Table I original reaction number should be represented in the reference index, including channels that only have citations and no explicit rate expression.
- `validation`: Table I records require original reaction number and channel id.
- `docs/devlog`: unresolved multi-channel findings should become specific issues.

Current required behavior:

- Keep `data/staged/lee2020_table_i_reference.json` as the full non-canonical reference table.
- Keep all reference records disabled by default.
- If one original number has multiple channels, each channel must remain a separate record.
- Do not promote records to `data/canonical/` until human audit confirms reaction equation, channel count, unit, expression, and source references.

How to verify:

```powershell
$env:PYTHONPATH='src'
python -m he_cr_model.cli audit-data
python -m pytest tests/test_reaction_audit.py
```

Expected result:

- Known OCR issue `LEE2020_T1_R23_OCR_CHECK` is still flagged.
- No enabled unverified data exists.
- `data/staged/lee2020_table_i_reference.json` contains original reaction numbers 1-25.

Resolution criteria:

- Human compares `data/staged/lee2020_table_i_reference.json` against the original Lee Table I and marks each record as audited, corrected, or requiring primary-source review.

Human audit notes already received:

- `LEE2020_T1_R06_REF` represents many AI reactions and must be expanded/linked to Table II records, not treated as a single concrete channel.
- `LEE2020_T1_R08_CH1_REF` through `LEE2020_T1_R08_CH3_REF` had wrong products and have been manually corrected in the staged reference table.
- `LEE2020_T1_R13_CH1_REF`, `LEE2020_T1_R13_CH2_REF`, `LEE2020_T1_R14_REF`, and `LEE2020_T1_R15_REF` had reactant/product transcription issues and have been manually corrected in the staged reference table.

Follow-up requirement:

- Record-level audit status is needed. A future data update should add fields such as `audit_status`, `audited_by`, `audit_date`, and `audit_notes` so corrected records are distinguishable from unaudited staged records.

## ISSUE-006 Lee Table I reaction 6 must expand to Table II AI channels

Status: open

Problem:

`LEE2020_T1_R06_REF` is a reference-level row for `He(p) + He -> He2+ + e-`, with `rate_expression: Table II`. It does not represent one concrete reaction. Lee Table II gives state-specific AI rates, so reaction 6 must be linked to or expanded into the Table II channels before it can be used in a species balance.

Where:

- Reference row: `data/staged/lee2020_table_i_reference.json`, record `LEE2020_T1_R06_REF`
- Canonical AI rates: `data/canonical/lee2020_table_ii_ai.json`
- Loader: `src/he_cr_model/data_loader.py`
- Reaction model: `src/he_cr_model/reactions.py`

Affected modules:

- `data`: Table I reaction 6 is an umbrella entry; Table II contains concrete rates.
- `solver`: species source/loss construction must consume concrete Table II channels, not the umbrella reference row.

Current required behavior:

- Keep `LEE2020_T1_R06_REF` disabled.
- Do not use the umbrella reaction directly in calculations.
- Use only reviewed concrete AI records from `data/canonical/lee2020_table_ii_ai.json` for v0.1.0 AI sanity checks.

Resolution criteria:

- Add explicit linkage metadata from `LEE2020_T1_R06_REF` to Table II AI records.
- Ensure every concrete AI channel has reactants/products and target level mapping suitable for species balance assembly.

## ISSUE-007 Lee Table I reaction 9 unit ambiguity

Status: open

Problem:

Human audit flagged possible unit errors for:

- `LEE2020_T1_R09_CH1_REF`
- `LEE2020_T1_R09_CH2_REF`

The current staged reference table uses `cm^6/s` because the parsed row shows two He collision partners, but the auditor suspects the unit may be `cm^3/s`. This must be checked against the original PDF and/or reference 28 before any use.

Where:

- Data file: `data/staged/lee2020_table_i_reference.json`
- Records: `LEE2020_T1_R09_CH1_REF`, `LEE2020_T1_R09_CH2_REF`

Current required behavior:

- Keep both records disabled.
- Do not promote them to canonical until unit is resolved.

Resolution criteria:

- Human verifies reaction molecularity and units from Lee original table and reference 28.

## ISSUE-008 Project-wide species, variable, and unit convention is missing

Status: open

Problem:

Several Lee Table I rate expressions mix `Te` and `Tg`, and the table note says electron temperature `Te` and gas temperature `Tg` are in eV and K unless specified otherwise. However, specific rows override this. For example:

- `LEE2020_T1_R19_CH1_REF` notes `Te(K)`.
- `LEE2020_T1_R21_CH2_REF` uses `(Tg/Te)^2` but does not explicitly say `Te(K)` in the parsed row.

The project currently has no single convention document defining:

- internal electron temperature unit;
- internal gas temperature unit;
- density units;
- rate coefficient units;
- species notation such as `He2+` vs `He2*`;
- how to encode row-specific unit overrides.

Where:

- Global rule: `AGENTS.md`
- Data rule: `.agents/rules/data-agent.md`
- Affected data: `data/staged/lee2020_table_i_reference.json`
- Future doc needed: `docs/UNITS_AND_SPECIES.md` or equivalent

Current required behavior:

- Keep default internal `Te` as eV and `Tg` as K, as stated in `AGENTS.md`.
- For rows that require `Te(K)`, record explicit conversion requirements in data notes or structured fields before use.
- Do not evaluate rate expressions with ambiguous temperature units.

Resolution criteria:

- Create a project-wide unit/species convention document.
- Add schema fields for expression variable units or per-record unit overrides.
- Add tests that reject ambiguous `Te` use in enabled rate expressions.

## ISSUE-009 Reaction stoichiometry parsing and CR source/loss assembly is not implemented

Status: open

Problem:

The project goal is to solve collisional-radiative species balance equations. For each species `x`, the solver must parse the full reaction set, identify reactants and products, and add source/loss terms according to stoichiometry and rate coefficients.

This is not implemented yet. Current `src/he_cr_model/solver.py` only contains `apply_enabled_ai_losses`, a v0.1.0 sanity helper that applies verified AI loss to seed populations. It does not parse arbitrary reaction equations, does not build source/loss terms for all species, and does not assemble the full CR matrix.

Where:

- Current solver: `src/he_cr_model/solver.py`
- Current reaction model: `src/he_cr_model/reactions.py`
- Staged reaction source: `data/staged/lee2020_table_i_reference.json`
- Canonical AI data: `data/canonical/lee2020_table_ii_ai.json`

Affected modules:

- `reactions`: needs structured reactants/products instead of only equation strings.
- `validation`: must validate stoichiometry and species names.
- `solver`: must assemble production and consumption terms from structured reactions.
- `rates`: must evaluate rate expressions with explicit variable units.
- `tests`: must cover species source/loss sign and stoichiometric coefficients.

Current required behavior:

- Do not claim the project solves the full CR equation.
- Keep `scan` fail-closed for quantitative CR reproduction.

Resolution criteria:

- Add a structured reaction schema with `reactants`, `products`, stoichiometric coefficients, species ids, and rate law order.
- Implement parser or manual structured records for the Lee reaction set.
- Build a source/loss assembler that can compute contributions for each species.
- Add tests using simple reactions to confirm production/consumption signs and stoichiometric multipliers.

## ISSUE-004 Electron-impact source data is missing from v0.1.0

Status: open

Problem:

The scaffold does not include verified electron-impact excitation, de-excitation, or ionization source data. These are required for a quantitative CR model and for a real Fig. 3/Fig. 5 reproduction. v0.1.0 intentionally avoids importing Goto/Ralchenko or other external sources.

Where:

- Manual review file: `data/staged/manual_review_required.json`
- Relevant entries: `EXT_RALCHENKO_2008_ELECTRON_COLLISION`
- Solver fail-closed hook: `src/he_cr_model/solver.py`
- CLI behavior: `src/he_cr_model/cli.py`, command `scan`

Affected modules:

- `data`: missing source data remains external-review work.
- `rates`: no electron-impact rate calculator is enabled.
- `solver`: only a minimal AI-loss sanity helper exists.
- `harness`: scan must fail closed rather than invent source terms.

Current required behavior:

- `he-cr scan` must fail closed.
- Do not add placeholder numeric source terms.

How to verify:

```powershell
$env:PYTHONPATH='src'
python -m he_cr_model.cli scan
python -m pytest tests/test_cli.py
```

Expected result:

- `scan` returns fail-closed messaging.
- CLI tests pass.

Resolution criteria:

- Future roadmap approval allows importing verified electron collision data with provenance.

## ISSUE-005 Lee Table I reaction 23 OCR/units unreliable

Status: open

Problem:

The parsed Lee text for Table I reaction 23 contains an unreliable OCR expression. It is kept as an explicit disabled placeholder so data audit can catch it.

Where:

- Data file: `data/staged/lee2020_table_i.json`
- Record: `LEE2020_T1_R23_OCR_CHECK`
- Validation module: `src/he_cr_model/validation.py`
- Tests: `tests/test_reaction_audit.py`

Affected modules:

- `data`: record remains disabled.
- `validation`: must flag `OCR_CHECK_REQUIRED` and inconsistent/missing units.

Current required behavior:

- Keep `rate_expression: OCR_CHECK_REQUIRED`.
- Keep `unit: MISSING`.
- Keep `enabled_by_default: false`.

How to verify:

```powershell
$env:PYTHONPATH='src'
python -m he_cr_model.cli audit-data
python -m pytest tests/test_reaction_audit.py
```

Expected result:

- `audit-data` reports `LEE2020_T1_R23_OCR_CHECK`.
- Tests confirm the OCR issue is flagged.

Resolution criteria:

- Human checks the original table or primary reference and replaces the placeholder with verified expression, unit, source details, and valid range.
