# Agent Router

Use this file to choose the smallest relevant rule file before changing code.

- `data/`: read `.agents/rules/data-agent.md`.
- `schemas/`: read `.agents/rules/schema-agent.md`.
- `configs/`: read `.agents/rules/harness-agent.md`.
- `src/he_cr_model/levels.py`, `src/he_cr_model/reactions.py`: read `.agents/rules/model-agent.md`.
- `src/he_cr_model/rates.py`, `src/he_cr_model/solver.py`, `src/he_cr_model/spectra.py`, `src/he_cr_model/fit.py`: read `.agents/rules/solver-agent.md`.
- `harnesses/` and CLI run orchestration: read `.agents/rules/harness-agent.md`.
- `tests/`: read `.agents/rules/test-agent.md`.
- `README.md`, `docs/`, `ROADMAP.md`, `CHANGELOG.md`: read `.agents/rules/docs-agent.md`.

When a change touches multiple areas, read every matching module rule.
