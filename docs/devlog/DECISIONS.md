# Decisions

## DEC-001 Initial roadmap scope

Decision: `ROADMAP.md` contains only v0.1.0.
Reason: future versions require human review of v0.1.0 outputs, data gaps, and implementation limitations.

## DEC-002 He2+ and He2* handling

Decision: `He2+` and `He2*` are auxiliary species only in v0.1.0 and are not fitted variables.
Reason: four target He lines cannot constrain these densities in the initial model.

## DEC-003 Data layer hierarchy

Decision: data is split into `data/raw_sources/`, `data/staged/`, and `data/canonical/`.
Reason: raw source snapshots, extracted-but-unverified records, and human-reviewed records need different trust levels and loading behavior.
