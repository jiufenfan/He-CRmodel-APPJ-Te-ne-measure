# Data Layout

The data directory is intentionally split into three layers.

## `raw_sources/`

Raw or source-nearest material. These files are not consumed directly by the model.

- `raw_sources/lee2020/`: Lee 2020 source snapshots from the parsed paper.
- `raw_sources/nist/`: reserved for future NIST ASD exports or query snapshots.
- `raw_sources/literature_pdfs/`: reserved for future primary-reference PDFs or extraction manifests.

## `staged/`

Extracted data that is useful for review but is not fully canonical. Staged records may be incomplete, OCR-uncertain, missing branch rates, or require primary-source review. They must stay disabled unless verified.

Examples:

- `staged/lee2020_table_i.json`
- `staged/spectral_lines_seed.json`
- `staged/manual_review_required.json`

## `canonical/`

Human-reviewed data allowed to participate in default calculations when each record also has `enabled_by_default: true`.

Examples:

- `canonical/lee2020_table_ii_ai.json`

Rules:

- Do not move data from `staged/` to `canonical/` without human review.
- Keep original source pointers in every scientific record.
- Preserve Lee original reaction numbers and channel ids when entering Table I reaction data.
