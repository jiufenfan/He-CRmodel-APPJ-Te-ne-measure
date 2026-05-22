# Reaction Network And Species Balance Design

Date: 2026-05-22

Scope: design for generating an auditable helium collisional-radiative reaction
network from Lee 2020 reaction text, NIST He I level/line data, and future
primary-source collision data.

## Status And Assumptions

This design treats ISSUE-009 as an independent architecture problem. It can be
designed without waiting for all scientific data issues to finish. Actual
solver-ready quantitative channels still require reviewed data and explicit
provenance before they are enabled.

The project uses a two-layer level representation:

- Solver populations use LS-term species, such as `He(2^3S)`, `He(3^3P)`,
  `He+`, `He2+`, and `e`.
- Raw spectroscopic data preserves J-resolved NIST states and lines, including
  configuration, term, J, energy, wavelength, and Einstein A values.

The reaction network is reaction-first. Lee 2020 defines the reaction-family
backbone. External data sources provide concrete level mappings, transition
probabilities, cross sections, or rate coefficients for reaction families that
Lee 2020 explicitly declares but does not fully enumerate.

The system must not generate new physics channels merely because they are
plausible. It may only expand a reaction template when a source record declares
the reaction family and an explicit expansion policy exists.

## Design 1: Text To Structured Reactions And Species

Raw reaction text is not solver input. It is provenance-bearing source material.
The system should keep three separate representations.

### Raw Reaction Record

This layer preserves source-nearest text:

- original reaction string
- Lee table number and original reaction number
- channel id when one Lee row has multiple product channels
- source citation, page, table, notes, and OCR status
- review status and enabled flag

Example:

```text
He(p) -> He(q) + hv
```

This layer answers only: what did the source say?

### Structured Reaction Template

This layer parses the raw record into machine-readable semantics:

- `reaction_id`
- `original_reaction_no`
- `channel_id`
- `reaction_family`
- `reactants`
- `products`
- `placeholders`
- `rate_payload_ref`
- `source_record_ref`
- `review_status`
- `enabled_by_default`

The `reaction_family` field is mandatory. The initial controlled vocabulary
should include:

- `spontaneous_radiation`
- `radiative_absorption_or_stimulated`
- `electron_impact_excitation`
- `electron_impact_deexcitation`
- `electron_impact_ionization`
- `three_body_recombination`
- `radiative_recombination`
- `dissociative_recombination`
- `associative_ionization`
- `penning_like`
- `heavy_particle_quenching`
- `unknown_or_composite`

### Placeholder Expansion Rule

Symbols such as `He(p)` and `He(q)` must not become species by free string
parsing. They refer to a controlled domain:

- `p`: an upper or source He I LS-term level selected from the solver level
  registry.
- `q`: a lower or destination He I LS-term level selected from the solver
  level registry and filtered by the family-specific policy.

The raw template remains intact. Expansion creates separate concrete channels
that reference the template.

### Species Generation

The system may generate species candidates from structured reactions, but final
solver species must pass through the species registry.

Rules:

- Solver species are LS-term level ids and non-level species from the registry.
- J-resolved states are spectroscopic states, not solver species.
- `hv` is an event marker, not a solved particle species.
- Placeholder species must be expanded through registry-backed policies.
- Unknown species names fail validation or remain disabled.

## Design 2: Structured Channels To Source And Loss Terms

The solver consumes concrete channels, not raw reaction strings.

### Concrete Channel

Each expanded or already concrete reaction becomes:

- `channel_id`
- `template_id`
- `family`
- `reactants`: species id plus stoichiometric coefficient
- `products`: species id plus stoichiometric coefficient
- `directionality`
- `energy_order_constraint`
- `rate_law`
- `rate_payload`
- `rate_origin`
- `provenance`
- `review_status`
- `enabled_by_default`

For each channel `c`, define a scalar rate:

```text
R_c = f_c(n, Te, Tg, ...)
```

For each species `s`, the source/loss contribution is:

```text
dn_s/dt += nu[s, c] * R_c
```

where `nu[s, c]` is product stoichiometry minus reactant stoichiometry.

### Family-Specific Rate Evaluation

Different reaction families require different rate evaluators.

#### Spontaneous Radiation

Spontaneous radiation is one-way in the default CR model:

```text
He(upper) -> He(lower) + hv
```

Constraint:

```text
E_upper > E_lower
```

Rate:

```text
R = Aki * n_upper
```

Contributions:

- upper level: `-R`
- lower level: `+R`
- photon marker: no species-balance equation

The reverse low-to-high process is not spontaneous radiation. Absorption or
stimulated emission requires a separate `radiative_absorption_or_stimulated`
family and an explicit radiation-field model. It is disabled by default unless
future scope explicitly adds that physics.

#### Electron-Impact Excitation And Deexcitation

Electron-impact level transfer is directional, but both directions may exist as
separate concrete channels:

```text
e + He(low)  -> e + He(high)
e + He(high) -> e + He(low)
```

The excitation channel has `E_high > E_low`. The deexcitation channel is a
separate record, not an implicit reverse flag on the same channel.

If both directions are tabulated, each keeps its own provenance. If only one
direction is tabulated, a reverse channel may be generated only by an explicit
detailed-balance policy. Such a channel must carry:

- `rate_origin: derived_by_detailed_balance`
- the source channel id
- degeneracy and energy metadata used by the derivation
- review status proving that this derivation is allowed

Until that policy is approved, derived reverse channels remain disabled.

#### Electron-Impact Ionization

Example:

```text
e + He(i) -> 2e + He+
```

Rate:

```text
R = k_i_ion(Te) * n_e * n_i
```

Net stoichiometry:

- `He(i)`: `-1`
- `He+`: `+1`
- `e`: `+1`

#### Recombination And Heavy-Particle Channels

Recombination, associative ionization, Penning-like channels, and heavy-particle
quenching must preserve molecularity and collision partners. They must not be
flattened into a generic rate expression without explicit unit and density-order
metadata.

### Linear And Nonlinear Assembly

The network builder should classify solver-ready channels into:

- one-body linear terms, such as spontaneous radiation
- two-body nonlinear terms, such as electron-impact excitation
- three-body nonlinear terms, such as three-body recombination

This avoids forcing the entire CR system into a constant matrix. A steady-state
solver can still assemble residuals from a unified channel list.

### J-Resolved To LS-Term Mapping

Raw NIST states and lines stay J-resolved. Solver transfer channels use LS-term
levels.

The mapping layer must provide:

- `j_state_id -> ls_term_id`
- `j_resolved_line_id -> upper_j_state_id, lower_j_state_id`
- `ls_transition_id -> member_j_resolved_line_ids`
- aggregation policy and provenance

For spectrum diagnostics, the system may use J-resolved line data directly. For
population equations, the solver should use reviewed LS-term transfer channels
that reference their J-resolved member lines. Aggregation must not silently
sum unrelated lines.

## Design 3: End-To-End Pipeline

The full pipeline has six layers.

### 1. Raw Source Layer

Source-nearest files live under `data/raw_sources/`:

- Lee 2020 extracted tables or manually reviewed text
- NIST ASD level and line exports
- future primary-reference tables, cross sections, and manifests

This layer stores files, query parameters, citations, dates, and notes. It does
not decide whether data is solver-ready.

### 2. Parsed Source Layer

Each source is parsed into source-native structured records:

- NIST levels parsed from the level export
- NIST lines parsed from the line export
- Lee Table I parsed into raw reaction records
- future collision cross-section tables parsed as source-native data assets

This layer answers: what records were present in each source?

### 3. Registry Layer

Global registries define standard project identities:

- `species_registry`
- `solver_level_registry`
- `spectroscopic_state_registry`
- `reaction_template_registry`
- `rate_payload_registry`
- `data_asset_registry`

The registry layer is the only place that turns source names into project ids.

### 4. Expansion Layer

Expansion converts templates into concrete channels.

Allowed expansion modes:

- `none`: the template is already concrete.
- `enumerate_from_registry`: placeholders are replaced using a controlled
  registry domain.
- `enumerate_and_filter_by_external_data`: candidates are generated from a
  registry and kept only when matching reviewed external data exists.

For spontaneous radiation, the expansion policy is:

- start from a Lee-declared radiation template
- enumerate candidate upper/lower LS-term pairs
- require `E_upper > E_lower`
- require reviewed NIST-backed Aki mapping
- generate one concrete channel per reviewed LS-term transfer

### 5. Validation And Review Layer

Each concrete channel must pass validation before it can be solver-ready:

- every reactant and product is in the species registry
- units are explicit and consistent with reaction molecularity
- rate payload exists and is compatible with the family
- provenance points to source records and data assets
- review status allows quantitative use
- enabled flag is true
- directionality and energy constraints are satisfied

Validation should produce two outputs:

- `network_all`: includes disabled, incomplete, and review-needed channels
- `network_solver_ready`: includes only reviewed, enabled, fully bound channels

### 6. Solver Network Layer

The solver consumes:

- ordered solver species
- concrete solver-ready channels
- stoichiometry matrix
- rate evaluator bindings

The solver does not read raw CSV, Lee text, NIST exports, or PDF-derived tables.
It receives already validated objects.

## Source Roles

### Lee 2020

Lee Table I defines the reaction-family backbone. It can produce reaction
templates, placeholders, and candidate species references. It cannot by itself
produce a complete solver-ready network when rates, channels, or level mappings
are missing.

### NIST ASD

NIST ASD provides authoritative He I level and line data for:

- J-resolved spectroscopic states
- energy ordering
- wavelengths
- Einstein A coefficients
- mapping evidence for radiation channels

NIST should not create reaction families by itself. It concretizes Lee-declared
radiation templates.

### Primary Collision References

Collision references provide rate payloads:

- analytic rate coefficients
- tabulated rate coefficients
- cross sections
- Maxwellian-averaged tables
- derived data with documented assumptions

These payloads bind to already declared reaction templates or concrete
channels. Cross sections are upstream data; the solver should consume a rate
provider interface, not raw cross-section files directly.

## Implementation Sequence

The recommended implementation order is:

1. Define schema objects for species, solver levels, spectroscopic states,
   reaction templates, concrete channels, and rate payloads.
2. Add validation tests for unknown species, missing provenance, ambiguous
   units, invalid directionality, and disabled unreviewed data.
3. Implement Lee Table I template parsing without enabling quantitative use.
4. Implement NIST J-resolved level/line registry loading.
5. Implement LS-term mapping and reviewed aggregation records.
6. Implement controlled expansion for spontaneous radiation.
7. Implement the channel-to-stoichiometry assembler with toy reactions.
8. Implement family-specific rate evaluator interfaces.
9. Enable only reviewed solver-ready channels.

## Explicit Non-Goals

This design does not enable unreviewed staged data by default.

This design does not promote raw or staged NIST records to canonical data
without human review evidence.

This design does not generate reaction families from selection rules alone.

This design does not add low-to-high spontaneous radiation. Absorption and
stimulated radiative processes require a separate future model.

This design does not require the first solver implementation to solve the full
quantitative Lee 2020 reproduction problem. It first establishes audited network
construction and source/loss assembly.
