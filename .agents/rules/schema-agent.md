# Schema Agent Rule

- Schemas enforce fail-closed behavior.
- Missing source, unknown unit, unknown review status, or enabled unverified data must produce validation issues.
- Keep schema fields explicit and stable; changing a schema requires test updates and a devlog decision.
- Do not relax validation to make a run pass.
