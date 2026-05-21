# He CR Model Reproduction Scaffold

This project is a v0.1.0 scaffold for reproducing the model workflow of Lee 2020, *Study on helium atmospheric pressure plasma jet using collisional-radiative model*.

The initial version is intentionally conservative:

- Lee-only data where clearly readable.
- Unverified and OCR-uncertain data disabled by default.
- No NIST/LXCat fetching.
- No full quantitative reproduction claim.

See `ROADMAP.md` and `AGENTS.md` before making changes.

Current issue dashboard:

- `docs/devlog/ISSUE_DASHBOARD.md`

## Data Layout

Data is split into:

- `data/raw_sources/`: source-nearest material such as Lee parsed markdown, future NIST exports, or future literature PDF manifests.
- `data/staged/`: extracted but not fully verified data.
- `data/canonical/`: human-reviewed data allowed for default use.

## Local Development

Run tests:

```powershell
python -m pytest
```

Run the CLI without installing the package:

```powershell
$env:PYTHONPATH='src'
python -m he_cr_model.cli list-levels
python -m he_cr_model.cli list-reactions --all
python -m he_cr_model.cli spectrum
python -m he_cr_model.cli scan
```

After editable install, the configured entry point is:

```powershell
he-cr list-levels
```

`spectrum` and `scan` intentionally fail closed in v0.1.0 when verified transition probabilities or source terms are missing.
