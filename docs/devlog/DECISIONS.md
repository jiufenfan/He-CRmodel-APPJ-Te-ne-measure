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

## DEC-004 Separate human and agent issue views

Decision: `docs/devlog/ISSUE_DEPENDENCY_GRAPH.md` and `docs/devlog/ACTIVE_ISSUES.md` remain human-readable detailed references, while agents start from `docs/devlog/AGENT_ISSUE_ROUTER.md` and `docs/devlog/issue_dependencies.yaml`.
Reason: issue governance and scientific constraints must remain complete for human review, but routine agent work should load a minimal route file and a compact dependency file first to reduce context use without losing semantic coverage.
